# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 测试分层基类
# @Time   : 2026-04-01
# @Author : 毛鹏
"""
测试分层基类

提供三层测试架构：
- UnitTest: 单元测试（60%）- 单接口测试
- IntegrationTest: 集成测试（30%）- 模块间集成
- E2ETest: 端到端测试（10%）- 完整业务流程

使用示例：
    from auto_test.demo_project.test_cases import UnitTest, IntegrationTest, E2ETest

    class TestUserAPI(UnitTest):
        def test_create_user(self):
            result = self.api.user.create_user(username="test")
            self.assert_success(result)
            self.assert_field_equals(result, "data.username", "test")
"""

import time
from abc import ABC
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, Any, Optional, List, Callable, Type

import pytest


class TestLayerType(Enum):
    """测试分层类型"""

    UNIT = auto()  # 单元测试
    INTEGRATION = auto()  # 集成测试
    E2E = auto()  # 端到端测试


@dataclass
class TestCaseResult:
    """测试结果"""

    name: str
    layer: TestLayerType
    success: bool
    duration: float = 0.0
    message: str = ""
    data: Dict = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "layer": self.layer.name,
            "success": self.success,
            "duration": self.duration,
            "message": self.message,
            "data": self.data,
            "errors": self.errors,
        }


class TestContext:
    """
    统一测试上下文

    提供：
    - 数据创建/使用
    - 动作执行
    - 状态验证
    - 事件追踪

    使用示例：
        with self.context() as ctx:
            # 创建数据
            user = ctx.create(UserEntity, username="test")

            # 执行动作
            ctx.action("login", username="test", password="123456")

            # 验证状态
            ctx.expect_status("active")

            # 追踪事件
            ctx.event("login_success").was_fired()
    """

    def __init__(self, api=None, token: str = None):
        self.api = api
        self.token = token
        self._created_entities: List[Any] = []
        self._events: List[str] = []
        self._state: Dict[str, Any] = {}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()

    def create(self, entity_type: Type, **kwargs) -> Any:
        """创建实体"""
        # 延迟导入避免循环依赖
        from auto_test.demo_project.data_factory.strategies import APIStrategy

        strategy = APIStrategy(token=self.token)
        result = strategy.create(entity_type, **kwargs)

        if result.success and result.entity:
            self._created_entities.append(result.entity)
            return result.entity

        raise Exception(f"创建实体失败: {result.error_message}")

    def use(self, entity: Any) -> "TestContext":
        """使用已存在的实体"""
        self._state["current_entity"] = entity
        return self

    def action(self, action_name: str, **params) -> "TestContext":
        """执行动作"""
        # 记录动作
        self._events.append(f"action:{action_name}")

        # 这里可以扩展为实际的动作执行
        # 例如：调用API、触发事件等

        return self

    def expect_status(self, expected_status: str) -> "TestContext":
        """验证状态"""
        current = self._state.get("current_entity")
        if current:
            actual_status = getattr(current, "status", None)
            if actual_status != expected_status:
                raise AssertionError(
                    f"状态验证失败: 期望 {expected_status}, 实际 {actual_status}"
                )
        return self

    def expect_field(self, field_path: str, expected_value: Any) -> "TestContext":
        """验证字段值"""
        current = self._state.get("current_entity")
        if current:
            # 支持路径如 "data.username"
            value = current
            for part in field_path.split("."):
                value = (
                    getattr(value, part, None)
                    if hasattr(value, part)
                    else value.get(part) if isinstance(value, dict) else None
                )

            if value != expected_value:
                raise AssertionError(
                    f"字段验证失败: {field_path} 期望 {expected_value}, 实际 {value}"
                )
        return self

    def event(self, event_name: str) -> "EventExpectation":
        """事件追踪"""
        return EventExpectation(self, event_name)

    def cleanup(self):
        """清理创建的数据"""
        for entity in reversed(self._created_entities):
            try:
                # 尝试删除
                if hasattr(entity, "id") and entity.id:
                    # 这里可以调用删除API
                    pass
            except Exception:
                pass


class EventExpectation:
    """事件期望"""

    def __init__(self, context: TestContext, event_name: str):
        self.context = context
        self.event_name = event_name

    def was_fired(self) -> bool:
        """检查事件是否触发"""
        return f"event:{self.event_name}" in self.context._events

    def was_not_fired(self) -> bool:
        """检查事件是否未触发"""
        return not self.was_fired()


def case_data(data: Dict[str, Any]):
    """
    场景数据绑定装饰器

    将测试数据绑定到测试方法

    使用示例：
        class TestUserAPI(UnitTest):
            @case_data({
                "username": "admin",
                "password": "admin123",
                "expected_role": "admin"
            })
            def test_admin_login(self):
                # self.case_data 可用
                result = self.api.auth.login(
                    self.case_data["username"],
                    self.case_data["password"]
                )
                self.assert_success(result)
    """

    def decorator(func: Callable) -> Callable:
        func._case_data = data
        return func

    return decorator


class TestLayer(ABC):
    """
    测试分层基类

    所有测试层的基类，提供通用功能
    """

    LAYER: TestLayerType = None

    @pytest.fixture(autouse=True)
    def setup_test_layer(self, api_client):
        """设置测试层"""
        self.api = api_client
        self.token = getattr(api_client, "token", None)
        self._case_data: Optional[Dict] = None
        self._results: List[TestCaseResult] = []

    @property
    def layer_name(self) -> str:
        """获取层名称"""
        return self.LAYER.name if self.LAYER else "UNKNOWN"

    def context(self) -> TestContext:
        """创建测试上下文"""
        return TestContext(api=self.api, token=self.token)

    def assert_success(self, result: Dict, message: str = ""):
        """断言成功"""
        assert (
            result.get("code") == 200
        ), f"期望成功，实际: {result.get('code')} - {result.get('message', message)}"

    def assert_failure(
        self, result: Dict, expected_code: int = None, message: str = ""
    ):
        """断言失败"""
        if expected_code:
            assert (
                result.get("code") == expected_code
            ), f"期望错误码 {expected_code}，实际: {result.get('code')}"
        else:
            assert result.get("code") != 200, f"期望失败，实际成功"

    def assert_field_equals(self, result: Dict, field_path: str, expected_value: Any):
        """断言字段值相等"""
        data = result.get("data", {})

        # 支持路径如 "user.username"
        value = data
        for part in field_path.split("."):
            if isinstance(value, dict):
                value = value.get(part)
            else:
                value = getattr(value, part, None)

        assert (
            value == expected_value
        ), f"字段 {field_path} 期望 {expected_value}，实际 {value}"

    def assert_field_exists(self, result: Dict, field_path: str):
        """断言字段存在"""
        data = result.get("data", {})

        value = data
        for part in field_path.split("."):
            if isinstance(value, dict):
                if part not in value:
                    assert False, f"字段 {field_path} 不存在"
                value = value.get(part)
            else:
                if not hasattr(value, part):
                    assert False, f"字段 {field_path} 不存在"
                value = getattr(value, part)

        assert value is not None, f"字段 {field_path} 为空"

    def record_result(self, name: str, success: bool, **kwargs):
        """记录测试结果"""
        result = TestCaseResult(name=name, layer=self.LAYER, success=success, **kwargs)
        self._results.append(result)
        return result

    def get_results(self) -> List[TestCaseResult]:
        """获取所有结果"""
        return self._results


class UnitTest(TestLayer):
    """
    单元测试层（60%）

    特点：
    - 单接口测试
    - 最小依赖
    - 快速执行
    - 高覆盖率

    使用场景：
    - 验证单个API的正确性
    - 参数边界值测试
    - 错误码验证

    示例：
        class TestUserAPI(UnitTest):
            def test_create_user_success(self):
                result = self.api.user.create_user(username="test")
                self.assert_success(result)
                self.assert_field_exists(result, "id")

            def test_create_user_duplicate(self):
                # 先创建一个用户
                self.api.user.create_user(username="duplicate")
                # 再创建同名用户
                result = self.api.user.create_user(username="duplicate")
                self.assert_failure(result, expected_code=400)
    """

    LAYER = TestLayerType.UNIT

    def setup_method(self):
        """单元测试前置设置"""
        # 单元测试通常需要清理数据
        pass

    def teardown_method(self):
        """单元测试后置清理"""
        # 清理创建的数据
        pass


class IntegrationTest(TestLayer):
    """
    集成测试层（30%）

    特点：
    - 多模块集成
    - 依赖链验证
    - 数据一致性
    - 状态流转

    使用场景：
    - 审批流程测试
    - 数据流验证
    - 模块间交互

    示例：
        class TestApprovalWorkflow(IntegrationTest):
            def test_full_approval_flow(self):
                with self.context() as ctx:
                    # 创建报销单
                    reimb = ctx.create(ReimbursementEntity, amount=1000)

                    # 部门审批
                    ctx.action("dept_approve")
                    ctx.expect_status("dept_approved")

                    # 财务审批
                    ctx.action("finance_approve")
                    ctx.expect_status("finance_approved")

                    # CEO审批
                    ctx.action("ceo_approve")
                    ctx.expect_status("fully_approved")
    """

    LAYER = TestLayerType.INTEGRATION

    def setup_method(self):
        """集成测试前置设置"""
        # 准备测试数据链
        pass

    def run_scenario(self, scenario_class: Type["BaseScenario"], **kwargs) -> Any:
        """运行场景"""
        scenario = scenario_class(token=self.token)
        return scenario.execute(**kwargs)


class E2ETest(TestLayer):
    """
    端到端测试层（10%）

    特点：
    - 完整业务流程
    - 真实用户场景
    - 全链路验证
    - 性能关注

    使用场景：
    - 完整报销流程
    - 用户注册到使用全流程
    - 跨系统业务流程

    示例：
        class TestCompleteReimbursementFlow(E2ETest):
            def test_user_submit_to_payment(self):
                # 完整流程：用户注册 -> 提交报销 -> 多级审批 -> 打款
                with self.context() as ctx:
                    # 1. 用户注册
                    user = ctx.create(UserEntity, role="employee")

                    # 2. 提交报销
                    reimb = ctx.create(ReimbursementEntity, user_id=user.id)
                    ctx.action("submit")

                    # 3. 完整审批流程
                    ctx.run_scenario(FullApprovalWorkflowScenario)

                    # 4. 验证打款
                    ctx.expect_field("payment.status", "completed")
    """

    LAYER = TestLayerType.E2E

    def setup_method(self):
        """E2E测试前置设置"""
        # 准备完整环境
        pass

    def run_full_scenario(self, scenario_class: Type["BaseScenario"], **kwargs) -> Any:
        """运行完整场景"""
        return self.run_scenario(scenario_class, **kwargs)

    def measure_performance(self, func: Callable, **kwargs) -> tuple:
        """测量性能"""
        start = time.time()
        result = func(**kwargs)
        duration = time.time() - start
        return result, duration

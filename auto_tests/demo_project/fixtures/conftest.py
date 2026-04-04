# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: fixtures注册中心 - 新架构
# @Time   : 2026-03-31
# @Author : 毛鹏

"""
fixtures注册中心 - 新架构

此文件集中注册所有fixtures，便于管理和使用。
在测试文件中只需导入此模块即可使用所有fixtures。

使用示例：
    # test_example.py
    from auto_tests.demo_project.fixtures.conftest import *

    def test_with_user(test_user):
        assert test_user.id is not None
        assert test_user.username is not None

    def test_with_scenario(full_approval_workflow):
        assert full_approval_workflow.success
        reimbursement = full_approval_workflow.get_entity("reimbursement")
        assert reimbursement is not None
"""

# ========== 直接定义 test_context fixture ==========
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List, Optional, Type, Callable

import pytest

from auto_tests.demo_project.data_factory import BaseEntity
# ========== 认证模块fixtures ==========
from auto_tests.demo_project.fixtures.builders.auth_fixtures import (
    auth_builder,
    test_token,
    registered_user,
)
# ========== C模块构造器fixtures ==========
from auto_tests.demo_project.fixtures.builders.c_fixtures import (
    org_builder,
    budget_builder,
)
# ========== 总经理审批模块fixtures ==========
from auto_tests.demo_project.fixtures.builders.ceo_approval_fixtures import (
    ceo_approval_builder,
    fully_approved_reimbursement,
    ceo_rejected_reimbursement,
    ceo_id,
    workflow_data,
)
# ========== 数据模块fixtures ==========
from auto_tests.demo_project.fixtures.builders.data_fixtures import (
    data_builder,
    submitted_data,
)
# ========== 部门审批模块fixtures ==========
from auto_tests.demo_project.fixtures.builders.dept_approval_fixtures import (
    dept_approval_builder,
    dept_approved_reimbursement,
    dept_rejected_reimbursement,
    dept_manager_id,
)
# ========== 文件模块fixtures ==========
from auto_tests.demo_project.fixtures.builders.file_fixtures import (
    file_builder,
    temp_file,
    uploaded_file,
)
# ========== 财务审批模块fixtures ==========
from auto_tests.demo_project.fixtures.builders.finance_approval_fixtures import (
    finance_approval_builder,
    finance_approved_reimbursement,
    finance_rejected_reimbursement,
    finance_manager_id,
)
# ========== 订单模块fixtures ==========
from auto_tests.demo_project.fixtures.builders.order_fixtures import (
    order_builder,
    test_order,
    order_with_product,
)
# ========== 产品模块fixtures ==========
from auto_tests.demo_project.fixtures.builders.product_fixtures import (
    product_builder,
    test_product,
    product_list,
)
# ========== 报销申请模块fixtures ==========
from auto_tests.demo_project.fixtures.builders.reimbursement_fixtures import (
    reimbursement_builder,
    created_reimbursement,
    pending_reimbursement,
    multiple_reimbursements,
)
# ========== 系统模块fixtures ==========
from auto_tests.demo_project.fixtures.builders.system_fixtures import (
    system_builder,
    server_health,
    server_info,
)
# ========== 用户模块fixtures ==========
from auto_tests.demo_project.fixtures.builders.user_fixtures import (
    user_builder,
    test_user,
    new_user,
    admin_user,
    dept_manager_user,
    finance_manager_user,
    ceo_user,
)
# ========== 基础设施fixtures ==========
from auto_tests.demo_project.fixtures.infra.client import (
    api_client,
    authenticated_client,
    api_client_with_cleanup,
)
from auto_tests.demo_project.fixtures.infra.db import (
    db_session,
    db_transaction,
    clean_db_state,
)
from auto_tests.demo_project.fixtures.scenarios.approval_scenario_fixtures import (
    create_reimbursement_scenario,
    full_approval_scenario,
    rejection_scenario,
    full_approval_workflow,
    dept_rejected_workflow,
    finance_rejected_workflow,
    ceo_rejected_workflow,
    approval_scenarios,
    pending_at_dept,
    pending_at_finance,
    pending_at_ceo,
    multi_level_workflows,
)
# ========== 场景fixtures ==========
from auto_tests.demo_project.fixtures.scenarios.scenario_fixtures import (
    login_scenario,
    register_and_login_scenario,
    logged_in_token,
)


@dataclass
class TestContextRecord:
    """测试上下文记录"""

    entity_type: str
    entity_id: str
    entity: Any
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


class TestContext:
    """
    测试上下文 - 用于 pytest fixture

    职责：
    1. 追踪测试中创建的数据
    2. 自动清理测试数据
    3. 提供统一的上下文访问接口
    4. 支持级联清理

    Example:
        def test_example(test_context):
            user = test_context.create(UserEntity, username="test")
            result = test_context.action(user.login)
            assert test_context.expect(result.success).is_true()
    """

    def __init__(
            self,
            auto_cleanup: bool = True,
            cascade_cleanup: bool = False,
            enable_lineage: bool = True,
    ):
        self.auto_cleanup = auto_cleanup
        self.cascade_cleanup = cascade_cleanup
        self.enable_lineage = enable_lineage
        self._created: Dict[str, TestContextRecord] = {}
        self._created_by_type: Dict[str, List[str]] = {}
        self._data: Dict[str, Any] = {}

    def create(self, entity_class: Type[BaseEntity], **kwargs) -> BaseEntity:
        """创建实体"""
        entity = entity_class(**kwargs)

        # 生成唯一ID（如果实体没有有效ID）
        entity_id = str(uuid.uuid4())[:8]
        if hasattr(entity, "id") and entity.id:
            # 实体已有有效ID，使用它
            entity_id = str(entity.id)
        else:
            # 实体没有ID或ID为None，设置生成的ID
            entity.id = entity_id

        record = TestContextRecord(
            entity_type=entity_class.__name__,
            entity_id=entity_id,
            entity=entity,
            metadata=kwargs,
        )

        self._created[entity_id] = record

        entity_type = entity_class.__name__
        if entity_type not in self._created_by_type:
            self._created_by_type[entity_type] = []
        self._created_by_type[entity_type].append(entity_id)

        return entity

    def get(self, key: str) -> Any:
        """获取上下文中的值"""
        return self._data.get(key)

    def set(self, key: str, value: Any):
        """设置上下文中的值"""
        self._data[key] = value

    def get_created(self, entity_class: Type[BaseEntity]) -> Optional[BaseEntity]:
        """获取最后创建的指定类型实体"""
        entity_type = entity_class.__name__
        if entity_type in self._created_by_type and self._created_by_type[entity_type]:
            last_id = self._created_by_type[entity_type][-1]
            return self._created[last_id].entity
        return None

    def use(self, entity_class: Type[BaseEntity], **filters) -> Optional[BaseEntity]:
        """
        复用已创建的实体

        @param entity_class: 实体类
        @param filters: 过滤条件
        @return: 实体或 None
        """
        entity_type = entity_class.__name__
        if entity_type not in self._created_by_type:
            return None

        for entity_id in self._created_by_type[entity_type]:
            record = self._created[entity_id]
            entity = record.entity
            match = True
            for key, value in filters.items():
                if not hasattr(entity, key) or getattr(entity, key) != value:
                    match = False
                    break
            if match:
                return entity
        return None

    def action(self, action_func: Callable, *args, **kwargs) -> Any:
        """
        执行业务动作

        @param action_func: 业务函数
        @param args: 位置参数
        @param kwargs: 关键字参数
        @return: 执行结果
        """
        return action_func(*args, **kwargs)

    def expect(self, actual: Any) -> "ValueExpectation":
        """
        创建预期验证器

        @param actual: 实际值
        @return: 值预期验证器
        """
        return ValueExpectation(actual)

    def fire_event(self, event_name: str, priority: str = "normal", **metadata):
        """
        触发事件

        @param event_name: 事件名称
        @param priority: 优先级
        @param metadata: 元数据
        """
        if not hasattr(self, "_events"):
            self._events: Dict[str, Dict[str, Any]] = {}
        self._events[event_name] = {
            "fired": True,
            "priority": priority,
            "metadata": metadata,
        }

    def event(self, event_name: str) -> "EventExpectation":
        """
        获取事件预期验证器

        @param event_name: 事件名称
        @return: 事件预期验证器
        """
        if not hasattr(self, "_events"):
            self._events: Dict[str, Dict[str, Any]] = {}
        return EventExpectation(self._events.get(event_name, {}))

    def cleanup(self):
        """清理所有创建的数据"""
        if not self.auto_cleanup:
            return

        for entity_id in reversed(list(self._created.keys())):
            record = self._created[entity_id]
            entity = record.entity
            if hasattr(entity, "delete") and callable(getattr(entity, "delete")):
                try:
                    entity.delete()
                except Exception:
                    pass

        self._created.clear()
        self._created_by_type.clear()


class ValueExpectation:
    """值预期验证器"""

    def __init__(self, actual: Any):
        self.actual = actual

    def equals(self, expected: Any) -> bool:
        """验证等于"""
        return self.actual == expected

    def is_not_none(self) -> bool:
        """验证不为 None"""
        return self.actual is not None

    def is_true(self) -> bool:
        """验证为 True"""
        return self.actual is True

    def is_false(self) -> bool:
        """验证为 False"""
        return self.actual is False

    def contains(self, item: Any) -> bool:
        """验证包含"""
        return item in self.actual

    def matches(self, predicate: Callable[[Any], bool]) -> bool:
        """验证匹配条件"""
        return predicate(self.actual)


class EventExpectation:
    """事件预期验证器"""

    def __init__(self, event_data: Dict[str, Any]):
        self.event_data = event_data

    def was_fired(self) -> bool:
        """验证事件已触发"""
        return self.event_data.get("fired", False)

    def has_priority(self, priority: str) -> bool:
        """验证优先级"""
        return self.event_data.get("priority") == priority

    def has_metadata(self, key: str, value: Any = None) -> bool:
        """验证元数据"""
        metadata = self.event_data.get("metadata", {})
        if value is None:
            return key in metadata
        return metadata.get(key) == value


@pytest.fixture
def test_context(request):
    """
    test_context Fixture

    提供测试上下文，自动追踪和清理测试数据

    使用示例：
        def test_example(test_context):
            user = test_context.create(UserEntity, username="test")
            result = test_context.action(user.login)
            assert test_context.expect(result.success).is_true()
    """
    auto_cleanup = True
    cascade_cleanup = False

    marker = request.node.get_closest_marker("test_context_config")
    if marker:
        auto_cleanup = marker.kwargs.get("auto_cleanup", True)
        cascade_cleanup = marker.kwargs.get("cascade_cleanup", False)

    ctx = TestContext(auto_cleanup=auto_cleanup, cascade_cleanup=cascade_cleanup)

    yield ctx

    if auto_cleanup:
        ctx.cleanup()


__all__ = [
    # 基础设施
    "api_client",
    "authenticated_client",
    "api_client_with_cleanup",
    "test_context",
    "TestContext",
    "TestContextRecord",
    "ValueExpectation",
    "EventExpectation",
    "db_session",
    "db_transaction",
    "clean_db_state",
    # 用户模块
    "user_builder",
    "test_user",
    "new_user",
    "admin_user",
    "dept_manager_user",
    "finance_manager_user",
    "ceo_user",
    # 报销申请模块
    "reimbursement_builder",
    "created_reimbursement",
    "pending_reimbursement",
    "multiple_reimbursements",
    # C模块构造器
    "org_builder",
    "budget_builder",
    # 部门审批模块
    "dept_approval_builder",
    "dept_approved_reimbursement",
    "dept_rejected_reimbursement",
    "dept_manager_id",
    # 财务审批模块
    "finance_approval_builder",
    "finance_approved_reimbursement",
    "finance_rejected_reimbursement",
    "finance_manager_id",
    # 总经理审批模块
    "ceo_approval_builder",
    "fully_approved_reimbursement",
    "ceo_rejected_reimbursement",
    "ceo_id",
    "workflow_data",
    # 产品模块
    "product_builder",
    "test_product",
    "product_list",
    # 订单模块
    "order_builder",
    "test_order",
    "order_with_product",
    # 文件模块
    "file_builder",
    "temp_file",
    "uploaded_file",
    # 数据模块
    "data_builder",
    "submitted_data",
    # 认证模块
    "auth_builder",
    "test_token",
    "registered_user",
    # 系统模块
    "system_builder",
    "server_health",
    "server_info",
    # 场景
    "login_scenario",
    "register_and_login_scenario",
    "logged_in_token",
    "create_reimbursement_scenario",
    "full_approval_scenario",
    "rejection_scenario",
    "full_approval_workflow",
    "dept_rejected_workflow",
    "finance_rejected_workflow",
    "ceo_rejected_workflow",
    "approval_scenarios",
    "pending_at_dept",
    "pending_at_finance",
    "pending_at_ceo",
    "multi_level_workflows",
]

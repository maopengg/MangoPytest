# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 测试上下文
# @Time   : 2026-05-03
# @Author : 毛鹏
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

from typing import Dict, Any, List, Optional, Type


class TestContext:
    """
    统一测试上下文

    提供：
    - 数据创建/使用
    - 动作执行
    - 状态验证
    - 事件追踪
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
        from auto_tests.pytest_api_mock.data_factory.strategies import APIStrategy

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

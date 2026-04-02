# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: test_context Fixture - 测试上下文追踪和清理
# @Time   : 2026-04-01
# @Author : 毛鹏

"""
test_context Fixture 模块

提供 pytest fixture：test_context
- 自动追踪测试中创建的数据
- 自动清理测试数据
- 提供统一的上下文访问接口

使用示例：
    def test_example(test_context):
        # 创建数据
        user = test_context.create(UserEntity, username="test")
        
        # 执行业务操作
        result = test_context.action(user.login)
        
        # 验证结果
        assert test_context.expect(result.success).is_true()
        
        # 测试结束后自动清理
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List, Optional, Type, Callable

import pytest

from auto_test.demo_project.data_factory.context import Context
from auto_test.demo_project.data_factory import BaseEntity



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
    
    Attributes:
        auto_cleanup: 是否自动清理
        cascade_cleanup: 是否级联清理
        enable_lineage: 是否启用血缘追踪
        _records: 创建记录列表
        _data: 上下文数据存储
    """

    # 告诉 pytest 这不是测试类
    __test__ = False

    def __init__(
            self,
            auto_cleanup: bool = True,
            cascade_cleanup: bool = False,
            enable_lineage: bool = True
    ):
        """
        初始化测试上下文
        
        @param auto_cleanup: 是否自动清理
        @param cascade_cleanup: 是否级联清理
        @param enable_lineage: 是否启用血缘追踪
        """
        self.auto_cleanup = auto_cleanup
        self.cascade_cleanup = cascade_cleanup
        self.enable_lineage = enable_lineage

        # 创建记录
        self._records: List[TestContextRecord] = []
        self._records_by_type: Dict[str, List[TestContextRecord]] = {}

        # 上下文数据存储
        self._data: Dict[str, Any] = {}

        # 事件追踪
        self._events: Dict[str, Dict[str, Any]] = {}

        # 内部 Context 实例
        self._context: Optional[Context] = None

    @property
    def context(self) -> Optional[Context]:
        """获取内部 Context 实例"""
        if self._context is None:
            self._context = Context(
                auto_cleanup=self.auto_cleanup,
                cascade_cleanup=self.cascade_cleanup,
                enable_lineage=self.enable_lineage
            )
        return self._context

    def create(self, entity_class: Type[BaseEntity], **kwargs) -> BaseEntity:
        """
        创建实体并记录
        
        @param entity_class: 实体类
        @param kwargs: 实体属性
        @return: 创建的实体
        """
        # 使用内部 Context 创建
        entity = self.context.create(entity_class, **kwargs)

        # 记录创建
        record = TestContextRecord(
            entity_type=entity_class.__name__,
            entity_id=getattr(entity, 'id', str(uuid.uuid4())),
            entity=entity,
            metadata={"source": "test_context.create"}
        )
        self._add_record(record)

        return entity

    def use(self, entity_class: Type[BaseEntity], **filters) -> Optional[BaseEntity]:
        """
        复用已创建的实体
        
        @param entity_class: 实体类
        @param filters: 过滤条件
        @return: 实体或 None
        """
        return self.context.use(entity_class, **filters)

    def action(self, action_func: Callable, *args, **kwargs) -> Any:
        """
        执行业务动作
        
        @param action_func: 业务函数
        @param args: 位置参数
        @param kwargs: 关键字参数
        @return: 执行结果
        """
        return self.context.action(action_func, *args, **kwargs)

    def expect(self, actual: Any) -> 'ValueExpectation':
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
        self._events[event_name] = {
            "fired": True,
            "priority": priority,
            "timestamp": datetime.now(),
            "metadata": metadata
        }

        # 同时触发内部 Context 的事件
        if self.context:
            self.context.fire_event(event_name, priority=priority)

    def event(self, event_name: str) -> 'EventExpectation':
        """
        获取事件预期验证器
        
        @param event_name: 事件名称
        @return: 事件预期验证器
        """
        return EventExpectation(self._events.get(event_name, {}))

    def set(self, key: str, value: Any):
        """
        设置上下文数据
        
        @param key: 键
        @param value: 值
        """
        self._data[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """
        获取上下文数据
        
        @param key: 键
        @param default: 默认值
        @return: 值
        """
        return self._data.get(key, default)

    def get_all_created(self, entity_class: Type[BaseEntity] = None) -> List[Any]:
        """
        获取所有创建的实体
        
        @param entity_class: 实体类（可选，用于过滤）
        @return: 实体列表
        """
        if entity_class:
            entity_type = entity_class.__name__
            return [
                r.entity for r in self._records
                if r.entity_type == entity_type
            ]
        return [r.entity for r in self._records]

    def _add_record(self, record: TestContextRecord):
        """添加记录"""
        self._records.append(record)

        # 按类型索引
        if record.entity_type not in self._records_by_type:
            self._records_by_type[record.entity_type] = []
        self._records_by_type[record.entity_type].append(record)

    def cleanup(self):
        """
        清理测试数据
        
        按照创建顺序的逆序清理
        """
        # 清理内部 Context
        if self._context:
            self._context.cleanup()

        # 清理记录
        for record in reversed(self._records):
            entity = record.entity
            if hasattr(entity, 'mark_as_deleted'):
                entity.mark_as_deleted()
            elif hasattr(entity, 'delete') and callable(getattr(entity, 'delete')):
                try:
                    entity.delete()
                except:
                    pass

        self._records.clear()
        self._records_by_type.clear()
        self._data.clear()
        self._events.clear()

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        if self.auto_cleanup:
            self.cleanup()


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


# pytest fixture
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
    # 从 marker 获取配置
    auto_cleanup = True
    cascade_cleanup = False

    # 检查是否有自定义配置 marker
    marker = request.node.get_closest_marker("test_context_config")
    if marker:
        auto_cleanup = marker.kwargs.get("auto_cleanup", True)
        cascade_cleanup = marker.kwargs.get("cascade_cleanup", False)

    # 创建测试上下文
    ctx = TestContext(
        auto_cleanup=auto_cleanup,
        cascade_cleanup=cascade_cleanup
    )

    yield ctx

    # 测试结束后自动清理
    if auto_cleanup:
        ctx.cleanup()


# 配置 marker
@pytest.fixture(autouse=True)
def test_context_marker(request):
    """自动添加 test_context 相关 marker"""
    pass


def pytest_configure(config):
    """配置 pytest"""
    config.addinivalue_line(
        "markers",
        "test_context_config(auto_cleanup=True, cascade_cleanup=False): "
        "配置 test_context fixture"
    )


# 导出
__all__ = [
    "TestContext",
    "TestContextRecord",
    "ValueExpectation",
    "EventExpectation",
    "test_context",
]

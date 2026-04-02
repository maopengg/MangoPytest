# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: Context 对象 - 场景执行上下文
# @Time   : 2026-04-01
# @Author : 毛鹏

"""
Context 对象模块

提供场景执行时的统一上下文管理：
- ctx.create() - 创建实体
- ctx.use() - 获取/复用已有实体
- ctx.action() - 执行业务动作
- ctx.expect() - 验证预期结果
- ctx.event() - 验证事件触发
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Type, Any, Callable

try:
    from .entities.base_entity import BaseEntity
    from .lineage.tracker import DataLineageTracker, get_global_tracker
except ImportError:
    from entities.base_entity import BaseEntity
    from lineage.tracker import DataLineageTracker, get_global_tracker


@dataclass
class CreatedRecord:
    """创建记录"""
    entity_type: str
    entity_id: str
    entity: Any
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ActionRecord:
    """动作记录"""
    action_name: str
    target_entity: str
    result: Any
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EventRecord:
    """事件记录"""
    event_name: str
    priority: str = "normal"
    fired: bool = False
    timestamp: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class Context:
    """
    场景执行上下文
    
    管理场景执行过程中的：
    - 实体创建和复用
    - 业务动作执行
    - 预期结果验证
    - 事件触发追踪
    - 数据血缘记录
    
    Example:
        ctx = Context()
        
        # 创建实体
        user = ctx.create(User, username="test", role="admin")
        
        # 复用已有实体
        existing_user = ctx.use(User, role="employee")
        
        # 执行业务动作
        ctx.action(user.login, password="123456")
        
        # 验证预期
        ctx.expect(user.status).equals("active")
        
        # 验证事件
        ctx.event("user_created").was_fired()
    """

    def __init__(
            self,
            auto_cleanup: bool = True,
            cascade_cleanup: bool = False,
            enable_lineage: bool = True
    ):
        self.auto_cleanup = auto_cleanup
        self.cascade_cleanup = cascade_cleanup
        self.enable_lineage = enable_lineage

        # 存储创建的记录
        self._created: Dict[str, CreatedRecord] = {}
        self._created_by_type: Dict[str, List[str]] = {}

        # 存储动作记录
        self._actions: List[ActionRecord] = []

        # 存储事件记录
        self._events: Dict[str, EventRecord] = {}

        # 存储复用的实体
        self._reused: Dict[str, Any] = {}

        # 血缘追踪器
        self._lineage_tracker: Optional[DataLineageTracker] = None
        if enable_lineage:
            self._lineage_tracker = get_global_tracker()

    def create(
            self,
            entity_class: Type[BaseEntity],
            **kwargs
    ) -> BaseEntity:
        """
        创建实体
        
        Args:
            entity_class: 实体类
            **kwargs: 实体属性
        
        Returns:
            BaseEntity: 创建的实体
        
        Example:
            user = ctx.create(User, username="test", role="admin")
        """
        # 创建实体
        entity = entity_class(**kwargs)

        # 生成唯一ID
        entity_id = str(uuid.uuid4())[:8]
        if hasattr(entity, 'id') and entity.id:
            entity_id = str(entity.id)
        elif not hasattr(entity, 'id'):
            entity.id = entity_id

        # 记录创建
        record = CreatedRecord(
            entity_type=entity_class.__name__,
            entity_id=entity_id,
            entity=entity,
            metadata=kwargs
        )

        self._created[entity_id] = record

        # 按类型索引
        entity_type = entity_class.__name__
        if entity_type not in self._created_by_type:
            self._created_by_type[entity_type] = []
        self._created_by_type[entity_type].append(entity_id)

        # 记录血缘
        if self._lineage_tracker:
            self._lineage_tracker.record_creation(
                entity_type=entity_type.lower(),
                entity_id=entity_id,
                source="context_create",
                metadata=kwargs
            )

        return entity

    def use(
            self,
            entity_class: Type[BaseEntity],
            **filters
    ) -> Optional[BaseEntity]:
        """
        获取/复用已有实体
        
        如果存在符合条件的已创建实体，则复用；否则返回 None
        
        Args:
            entity_class: 实体类
            **filters: 过滤条件（属性名=值）
        
        Returns:
            Optional[BaseEntity]: 实体或 None
        
        Example:
            user = ctx.use(User, role="employee")
            budget = ctx.use(Budget, amount__gt=1000)
        """
        entity_type = entity_class.__name__

        # 查找已创建的实体
        if entity_type in self._created_by_type:
            for entity_id in self._created_by_type[entity_type]:
                record = self._created[entity_id]
                entity = record.entity

                # 检查过滤条件
                match = True
                for key, value in filters.items():
                    # 处理比较操作符
                    if key.endswith('__gt'):
                        attr_name = key[:-4]
                        if not hasattr(entity, attr_name) or getattr(entity, attr_name) <= value:
                            match = False
                            break
                    elif key.endswith('__lt'):
                        attr_name = key[:-4]
                        if not hasattr(entity, attr_name) or getattr(entity, attr_name) >= value:
                            match = False
                            break
                    elif key.endswith('__gte'):
                        attr_name = key[:-5]
                        if not hasattr(entity, attr_name) or getattr(entity, attr_name) < value:
                            match = False
                            break
                    elif key.endswith('__lte'):
                        attr_name = key[:-5]
                        if not hasattr(entity, attr_name) or getattr(entity, attr_name) > value:
                            match = False
                            break
                    else:
                        # 精确匹配
                        if not hasattr(entity, key) or getattr(entity, key) != value:
                            match = False
                            break

                if match:
                    # 记录复用
                    self._reused[entity_id] = entity
                    return entity

        return None

    def action(
            self,
            action_func: Callable,
            *args,
            **kwargs
    ) -> Any:
        """
        执行业务动作
        
        Args:
            action_func: 业务动作函数
            *args: 位置参数
            **kwargs: 关键字参数
        
        Returns:
            Any: 动作执行结果
        
        Example:
            ctx.action(user.login, password="123456")
            ctx.action(order.submit)
        """
        # 执行动作
        result = action_func(*args, **kwargs)

        # 记录动作
        action_name = getattr(action_func, '__name__', str(action_func))
        target_entity = ""

        # 尝试获取目标实体
        if args and hasattr(args[0], '__class__'):
            target_entity = args[0].__class__.__name__

        record = ActionRecord(
            action_name=action_name,
            target_entity=target_entity,
            result=result,
            metadata={"args": args, "kwargs": kwargs}
        )
        self._actions.append(record)

        return result

    def get_created(self, entity_class: Type[BaseEntity]) -> Optional[BaseEntity]:
        """
        获取最后创建的指定类型实体
        
        Args:
            entity_class: 实体类
        
        Returns:
            Optional[BaseEntity]: 最后创建的实体或 None
        """
        entity_type = entity_class.__name__

        if entity_type in self._created_by_type and self._created_by_type[entity_type]:
            last_id = self._created_by_type[entity_type][-1]
            return self._created[last_id].entity

        return None

    def get_all_created(self, entity_class: Optional[Type[BaseEntity]] = None) -> List[BaseEntity]:
        """
        获取所有创建的实体
        
        Args:
            entity_class: 实体类（可选，不提供则返回所有）
        
        Returns:
            List[BaseEntity]: 实体列表
        """
        if entity_class:
            entity_type = entity_class.__name__
            if entity_type in self._created_by_type:
                return [
                    self._created[eid].entity
                    for eid in self._created_by_type[entity_type]
                ]
            return []

        return [record.entity for record in self._created.values()]

    def event(self, event_name: str) -> 'EventExpectation':
        """
        获取事件期望对象
        
        Args:
            event_name: 事件名称
        
        Returns:
            EventExpectation: 事件期望对象
        
        Example:
            ctx.event("user_created").was_fired()
            ctx.event("sla_alert").was_fired(priority="high")
        """
        if event_name not in self._events:
            self._events[event_name] = EventRecord(event_name=event_name)

        return EventExpectation(self._events[event_name])

    def fire_event(
            self,
            event_name: str,
            priority: str = "normal",
            **metadata
    ):
        """
        触发事件
        
        Args:
            event_name: 事件名称
            priority: 优先级（low/normal/high/critical）
            **metadata: 事件元数据
        """
        self._events[event_name] = EventRecord(
            event_name=event_name,
            priority=priority,
            fired=True,
            timestamp=datetime.now(),
            metadata=metadata
        )

    def expect(self, actual: Any) -> 'ValueExpectation':
        """
        创建值期望对象
        
        Args:
            actual: 实际值
        
        Returns:
            ValueExpectation: 值期望对象
        
        Example:
            ctx.expect(user.status).equals("active")
            ctx.expect(order.amount).gt(1000)
        """
        return ValueExpectation(actual)

    def get(self, key: str) -> Any:
        """
        获取上下文中的值
        
        Args:
            key: 键名
        
        Returns:
            Any: 存储的值
        """
        # 尝试从创建的记录中获取
        if key in self._created:
            return self._created[key].entity

        # 尝试从事件记录中获取
        if key == "events":
            return self._events

        if key == "actions":
            return self._actions

        return None

    def cleanup(self):
        """清理所有创建的数据"""
        if not self.auto_cleanup:
            return

        # 按创建顺序的逆序清理
        for entity_id in reversed(list(self._created.keys())):
            record = self._created[entity_id]
            entity = record.entity

            # 如果实体有 delete 方法，调用它
            if hasattr(entity, 'delete') and callable(getattr(entity, 'delete')):
                try:
                    entity.delete()
                except Exception:
                    pass

        # 清空记录
        self._created.clear()
        self._created_by_type.clear()
        self._actions.clear()
        self._events.clear()
        self._reused.clear()

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.cleanup()
        return False


class EventExpectation:
    """事件期望"""

    def __init__(self, event_record: EventRecord):
        self.event_record = event_record

    def was_fired(self, priority: Optional[str] = None) -> bool:
        """
        验证事件是否被触发
        
        Args:
            priority: 期望的优先级（可选）
        
        Returns:
            bool: 是否触发
        """
        if not self.event_record.fired:
            return False

        if priority and self.event_record.priority != priority:
            return False

        return True

    def was_not_fired(self) -> bool:
        """验证事件未被触发"""
        return not self.event_record.fired


class ValueExpectation:
    """值期望"""

    def __init__(self, actual: Any):
        self.actual = actual

    def equals(self, expected: Any) -> bool:
        """验证等于"""
        return self.actual == expected

    def not_equals(self, expected: Any) -> bool:
        """验证不等于"""
        return self.actual != expected

    def gt(self, value: Any) -> bool:
        """验证大于"""
        return self.actual > value

    def gte(self, value: Any) -> bool:
        """验证大于等于"""
        return self.actual >= value

    def lt(self, value: Any) -> bool:
        """验证小于"""
        return self.actual < value

    def lte(self, value: Any) -> bool:
        """验证小于等于"""
        return self.actual <= value

    def contains(self, item: Any) -> bool:
        """验证包含"""
        return item in self.actual

    def is_not_none(self) -> bool:
        """验证不为 None"""
        return self.actual is not None

    def is_none(self) -> bool:
        """验证为 None"""
        return self.actual is None

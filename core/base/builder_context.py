# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: Builder执行上下文
# @Time   : 2026-04-04
# @Author : 毛鹏
"""
Builder执行上下文模块

用于：
1. 追踪创建的数据（用于清理）
2. 存储已解决的依赖（避免重复创建）
3. 级联清理控制
4. 策略选择
"""

from typing import Dict, Any, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .base_entity import BaseEntity
    from .base_builder import BaseBuilder


class BuilderContext:
    """
    Builder执行上下文

    用于：
    1. 追踪创建的数据（用于清理）
    2. 存储已解决的依赖（避免重复创建）
    3. 级联清理控制
    4. 策略选择
    """

    def __init__(
            self,
            strategy: Optional[Any] = None,
            cascade_cleanup: bool = False,
            auto_prepare_deps: bool = True
    ):
        """
        初始化上下文

        @param strategy: 数据创建策略
        @param cascade_cleanup: 是否级联清理上游依赖
        @param auto_prepare_deps: 是否自动准备依赖数据
        """
        self.strategy = strategy
        self.cascade_cleanup = cascade_cleanup
        self.auto_prepare_deps = auto_prepare_deps

        # 追踪创建的数据：{实体类型: [(实体ID, Builder实例), ...]}
        self._created_entities: Dict[str, List[tuple]] = {}

        # 已解决的依赖：{依赖类型: 实体实例}
        self._resolved_deps: Dict[str, 'BaseEntity'] = {}

        # Builder注册表（用于获取或创建依赖Builder）
        self._builder_registry: Dict[str, 'BaseBuilder'] = {}

    def track(self, entity_type: str, entity_id: Any, builder: 'BaseBuilder'):
        """追踪创建的实体"""
        if entity_type not in self._created_entities:
            self._created_entities[entity_type] = []
        self._created_entities[entity_type].append((entity_id, builder))

    def get_resolved_dep(self, dep_type: str) -> Optional['BaseEntity']:
        """获取已解决的依赖"""
        return self._resolved_deps.get(dep_type)

    def set_resolved_dep(self, dep_type: str, entity: 'BaseEntity'):
        """设置已解决的依赖"""
        self._resolved_deps[dep_type] = entity

    def register_builder(self, builder_type: str, builder: 'BaseBuilder'):
        """注册Builder"""
        self._builder_registry[builder_type] = builder

    def get_builder(self, builder_type: str) -> Optional['BaseBuilder']:
        """获取已注册的Builder"""
        return self._builder_registry.get(builder_type)

    def get_all_created(self) -> Dict[str, List[tuple]]:
        """获取所有创建的实体"""
        return self._created_entities.copy()

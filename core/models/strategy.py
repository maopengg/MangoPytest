# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 策略和 Builder 相关数据模型
# @Time   : 2026-05-03
# @Author : 毛鹏
from dataclasses import dataclass
from typing import Dict, List, Optional, Any


@dataclass
class StrategyResult:
    """策略执行结果"""
    success: bool
    entity: Optional[Any] = None
    entities: Optional[List[Any]] = None
    raw_data: Optional[Dict[str, Any]] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    @property
    def data(self) -> Optional[Dict[str, Any]]:
        """获取原始数据"""
        return self.raw_data

    def get_entity(self) -> Optional[Any]:
        """获取单个实体"""
        return self.entity

    def get_entities(self) -> List[Any]:
        """获取实体列表"""
        return self.entities or []


@dataclass
class BuilderContext:
    """Builder执行上下文"""

    def __init__(
            self,
            strategy: Optional[Any] = None,
            cascade_cleanup: bool = False,
            auto_prepare_deps: bool = True
    ):
        self.strategy = strategy
        self.cascade_cleanup = cascade_cleanup
        self.auto_prepare_deps = auto_prepare_deps
        self._created_entities: Dict[str, List[tuple]] = {}
        self._resolved_deps: Dict[str, Any] = {}
        self._builder_registry: Dict[str, Any] = {}

    def track(self, entity_type: str, entity_id: Any, builder: Any):
        """追踪创建的实体"""
        if entity_type not in self._created_entities:
            self._created_entities[entity_type] = []
        self._created_entities[entity_type].append((entity_id, builder))

    def get_resolved_dep(self, dep_type: str) -> Optional[Any]:
        """获取已解决的依赖"""
        return self._resolved_deps.get(dep_type)

    def set_resolved_dep(self, dep_type: str, entity: Any):
        """设置已解决的依赖"""
        self._resolved_deps[dep_type] = entity

    def register_builder(self, builder_type: str, builder: Any):
        """注册Builder"""
        self._builder_registry[builder_type] = builder

    def get_builder(self, builder_type: str) -> Optional[Any]:
        """获取已注册的Builder"""
        return self._builder_registry.get(builder_type)

    def get_all_created(self) -> Dict[str, List[tuple]]:
        """获取所有创建的实体"""
        return self._created_entities.copy()

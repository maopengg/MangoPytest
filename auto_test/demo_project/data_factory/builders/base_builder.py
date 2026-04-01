# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: Builder基类 - 使用Entity的新版本
# @Time   : 2026-03-31
# @Author : 毛鹏
from abc import ABC, abstractmethod
from typing import List, Optional, TypeVar, Generic

from ..entities.base_entity import BaseEntity

T = TypeVar("T", bound=BaseEntity)


class BaseBuilder(ABC, Generic[T]):
    """
    Builder基类（新版本）

    职责：
    1. 构造实体数据
    2. 调用API创建/更新/删除数据
    3. 管理实体生命周期
    4. 自动清理创建的数据

    使用示例：
        class UserBuilder(BaseBuilder[UserEntity]):
            def build(self, **kwargs) -> UserEntity:
                return UserEntity(**kwargs)

            def create(self, **kwargs) -> UserEntity:
                # 调用API创建
                pass
    """

    def __init__(self, token: str = None, factory=None):
        """
        初始化Builder

        @param token: 认证token
        @param factory: 数据工厂实例
        """
        self.token = token
        self.factory = factory
        self._created_entities: List[BaseEntity] = []

    @abstractmethod
    def build(self, **kwargs) -> T:
        """
        构造实体（不调用API）

        @param kwargs: 构造参数
        @return: 实体实例
        """
        pass

    @abstractmethod
    def create(self, **kwargs) -> Optional[T]:
        """
        创建实体（调用API）

        @param kwargs: 创建参数
        @return: 创建后的实体（含ID）
        """
        pass

    def _register_created(self, entity: BaseEntity):
        """
        注册创建的实体（用于后续清理）

        @param entity: 实体实例
        """
        if entity and entity.id:
            self._created_entities.append(entity)

    def cleanup(self):
        """
        清理创建的数据

        子类可重写此方法自定义清理逻辑
        """
        # 默认实现：按创建顺序的逆序清理
        for entity in reversed(self._created_entities):
            try:
                self._delete_entity(entity)
            except Exception:
                pass  # 忽略清理错误

        self._created_entities.clear()

    def _delete_entity(self, entity: BaseEntity):
        """
        删除单个实体

        子类应重写此方法实现具体的删除逻辑

        @param entity: 要删除的实体
        """
        # 默认实现：标记为删除
        entity.mark_as_deleted()

    def get_created_entities(self) -> List[BaseEntity]:
        """
        获取所有创建的实体

        @return: 实体列表
        """
        return self._created_entities.copy()

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.cleanup()

# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: Pydantic Builder 基类 - 新五层架构
# @Time   : 2026-04-06
# @Author : 毛鹏
"""
Pydantic Builder 基类模块 - 新五层架构

L2 构造器层，职责：
1. 接收 L3 Entity
2. 调用 entity.to_api_payload() 获取 Dict
3. 调用 L1 API 创建/更新/删除数据
4. 更新 Entity 的响应字段（id, status 等）
5. 记录创建的 ID，支持 cleanup() 清理

使用示例：
    from core.base.pydantic_builder import PydanticBuilder

    class OrderBuilder(PydanticBuilder[OrderEntity]):
        def create_order(self, entity: OrderEntity) -> OrderEntity:
            payload = entity.to_api_payload()  # L3 提供
            result = demo_project.order.create_order(payload)  # L1
            entity.update_from_response(result["data"])  # 更新响应字段
            self._track_entity(entity)  # 追踪用于清理
            return entity
"""

from abc import ABC
from typing import Any, Dict, Generic, List, Optional, TypeVar, Type


T = TypeVar("T", bound="PydanticEntity")


class PydanticBuilder(ABC, Generic[T]):
    """
    Pydantic Builder 基类 - L2 构造器层

    接收 L3 Entity，调用 to_api_payload() 后传给 L1

    Attributes:
        token: 认证 token
        _created_entities: 创建的实体列表（用于清理）
    """

    # Entity 类型（子类重写）
    ENTITY_CLASS: Type[T] = None

    def __init__(self, token: Optional[str] = None):
        """
        初始化 Builder

        @param token: 认证 token
        """
        self.token = token
        self._created_entities: List[T] = []

        # 设置 API token
        if token:
            self._set_api_token(token)

    def _set_api_token(self, token: str) -> None:
        """设置 API token"""
        # 延迟导入避免循环导入
        from auto_tests.demo_project.api_manager import demo_project

        # 设置全局 token（所有模块共享）
        demo_project.set_token(token)

    def _track_entity(self, entity: T) -> None:
        """
        追踪创建的实体（用于清理）

        @param entity: 创建的实体
        """
        self._created_entities.append(entity)

    def cleanup(self) -> None:
        """
        清理所有创建的实体

        子类应重写此方法实现具体的清理逻辑
        """
        for entity in reversed(self._created_entities):
            if entity.id is not None:
                self._delete_entity(entity)
        self._created_entities.clear()

    def _delete_entity(self, entity: T) -> None:
        """
        删除实体 - 子类重写

        @param entity: 要删除的实体
        """
        pass

    def create(self, **kwargs) -> T:
        """
        创建实体 - 便捷方法

        使用 kwargs 创建 Entity，然后调用 API

        @param kwargs: Entity 字段
        @return: 创建的实体
        """
        entity = self.ENTITY_CLASS(**kwargs)
        return self.create_entity(entity)

    def create_entity(self, entity: T) -> T:
        """
        创建实体 - 子类必须重写

        @param entity: L3 Entity
        @return: 创建后的实体（包含响应字段）
        """
        raise NotImplementedError("子类必须重写 create_entity 方法")

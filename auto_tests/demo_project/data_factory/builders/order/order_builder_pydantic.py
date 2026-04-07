# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 订单构造器 - Pydantic 版本 (L2 构造器层)
# @Time   : 2026-04-06
# @Author : 毛鹏
"""
订单构造器 - L2 构造器层

接收 L3 Entity，调用 to_api_payload() 后传给 L1
"""

from typing import Any, Dict, List, Optional

from auto_tests.demo_project.api_manager import demo_project
from auto_tests.demo_project.data_factory.entities.order_pydantic import OrderEntity
from core.base import PydanticBuilder


class OrderBuilder(PydanticBuilder[OrderEntity]):
    """
    订单构造器 - L2 构造器层
    
    对应 /orders 接口
    
    使用示例：
        # 使用 Entity 创建订单
        order = OrderEntity.with_product(product_id=1, quantity=2)
        builder = OrderBuilder(token="xxx")
        created = builder.create_entity(order)
        
        # 便捷方法
        order = builder.create(product_id=1, user_id=1, quantity=2)
    """
    
    ENTITY_CLASS = OrderEntity
    
    def __init__(self, token: Optional[str] = None):
        """
        初始化 Builder
        
        @param token: 认证 token
        """
        super().__init__(token=token)
    
    def create_entity(self, entity: OrderEntity) -> OrderEntity:
        """
        创建订单实体
        
        @param entity: L3 OrderEntity
        @return: 创建后的 OrderEntity（包含 id 等响应字段）
        """
        payload = entity.to_api_payload()  # L3 提供
        result = demo_project.order.create_order(**payload)
        
        if result.get("code") == 200:
            # 更新 entity 的响应字段
            entity.update_from_response(result["data"])
            self._track_entity(entity)
            return entity
        
        raise RuntimeError(f"Failed to create order: {result.get('message')}")
    
    def get_by_id(self, order_id: int) -> Optional[OrderEntity]:
        """
        根据 ID 获取订单
        
        @param order_id: 订单 ID
        @return: OrderEntity 或 None
        """
        result = demo_project.order.get_order(order_id)
        
        if result.get("code") == 200:
            return OrderEntity.from_response(result["data"])
        
        return None
    
    def get_by_user(self, user_id: int) -> List[OrderEntity]:
        """
        根据用户 ID 获取订单
        
        @param user_id: 用户 ID
        @return: OrderEntity 列表
        """
        result = demo_project.order.get_orders_by_user(user_id)
        
        if result.get("code") == 200:
            return [OrderEntity.from_response(data) for data in result.get("data", [])]
        
        return []
    
    def pay(self, entity: OrderEntity) -> OrderEntity:
        """
        支付订单
        
        @param entity: L3 OrderEntity（必须包含 id）
        @return: 更新后的 OrderEntity
        """
        if entity.id is None:
            raise ValueError("Entity must have id to pay")
        
        result = demo_project.order.pay_order(entity.id)
        
        if result.get("code") == 200:
            entity.update_from_response(result["data"])
            return entity
        
        raise RuntimeError(f"Failed to pay order: {result.get('message')}")
    
    def cancel(self, entity: OrderEntity) -> OrderEntity:
        """
        取消订单
        
        @param entity: L3 OrderEntity（必须包含 id）
        @return: 更新后的 OrderEntity
        """
        if entity.id is None:
            raise ValueError("Entity must have id to cancel")
        
        result = demo_project.order.cancel_order(entity.id)
        
        if result.get("code") == 200:
            entity.update_from_response(result["data"])
            return entity
        
        raise RuntimeError(f"Failed to cancel order: {result.get('message')}")
    
    def _delete_entity(self, entity: OrderEntity) -> None:
        """
        删除实体
        
        @param entity: 要删除的订单实体
        """
        if entity.id:
            demo_project.order.delete_order(entity.id)

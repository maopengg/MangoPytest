# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 订单构造器 - 对应 /orders 接口
# @Time   : 2026-03-31
# @Author : 毛鹏
from typing import Dict, Any, List

from auto_test.demo_project.api_manager import demo_project
from ..base_builder import BaseBuilder
from ...registry import register_builder


@register_builder("order")
class OrderBuilder(BaseBuilder):
    """
    订单构造器
    对应 /orders 接口 (POST, GET, PUT, DELETE)
    """

    def __init__(self, token: str = None, factory=None):
        super().__init__(token=token, factory=factory)
        # 设置token到API模块
        if token:
            demo_project.order.set_token(token)

    def build(self, product_id: int = None, quantity: int = None,
              user_id: int = None, **kwargs) -> Dict[str, Any]:
        """
        构造订单数据（不调用API）
        @return: 订单数据字典
        """
        return {
            "product_id": product_id or 1,
            "quantity": quantity or 1,
            "user_id": user_id or 1
        }

    def create(self, product_id: int = None, quantity: int = None,
               user_id: int = None, **kwargs) -> Dict[str, Any]:
        """
        创建订单
        @return: 创建的订单数据
        """
        order_data = self.build(product_id, quantity, user_id)

        result = demo_project.order.create_order(
            product_id=order_data["product_id"],
            quantity=order_data["quantity"],
            user_id=order_data["user_id"]
        )

        if result.get("code") == 200:
            created_order = result["data"]
            return created_order
        return None

    def get_all(self) -> List[Dict[str, Any]]:
        """
        获取所有订单
        @return: 订单列表
        """
        result = demo_project.order.get_all_orders()
        if result.get("code") == 200:
            return result["data"]
        return []

    def get_by_id(self, order_id: int) -> Dict[str, Any]:
        """
        根据ID获取订单
        @param order_id: 订单ID
        @return: 订单数据
        """
        result = demo_project.order.get_order_by_id(order_id)
        if result.get("code") == 200:
            return result["data"]
        return None

    def update(self, order_id: int, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新订单信息
        @param order_id: 订单ID
        @param order_data: 订单数据
        @return: 更新后的订单数据
        """
        result = demo_project.order.update_order_info(
            order_id=order_id,
            **order_data
        )
        if result.get("code") == 200:
            return result["data"]
        return None

    def delete(self, order_id: int) -> bool:
        """
        删除订单
        @param order_id: 订单ID
        @return: 是否删除成功
        """
        result = demo_project.order.delete_order(order_id)
        if result.get("code") == 200:
            return True
        return False

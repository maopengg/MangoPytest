# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 订单构造器 - 对应 /orders 接口
# @Time   : 2026-03-31
# @Author : 毛鹏
from typing import Dict, Any, List, Optional
import uuid

from ..base_builder import BaseBuilder
from auto_test.demo_project.api_manager import demo_project
from ...registry import register_builder


@register_builder("order")
class OrderBuilder(BaseBuilder):
    """
    订单构造器
    对应 /orders 接口 (POST, GET, PUT, DELETE)
    """

    def __init__(self, token: str = None, factory=None):
        super().__init__(token, factory)

    def build(self, product_id: int = None, quantity: int = None,
              user_id: int = None) -> Dict[str, Any]:
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
               user_id: int = None) -> Dict[str, Any]:
        """
        创建订单
        @return: 创建的订单数据
        """
        order_data = self.build(product_id, quantity, user_id)

        api_data = self._create_api_data(
            url="/orders",
            method="POST",
            json_data=order_data
        )

        result = demo_project.order.create_order(api_data)
        if result.response and result.response.json().get("code") == 200:
            created_order = result.response.json()["data"]
            self._register_created(created_order)
            return created_order
        return None

    def get_all(self) -> List[Dict[str, Any]]:
        """
        获取所有订单
        @return: 订单列表
        """
        api_data = self._create_api_data(
            url="/orders",
            method="GET"
        )

        result = demo_project.order.get_all_orders(api_data)
        if result.response and result.response.json().get("code") == 200:
            return result.response.json()["data"]
        return []

    def get_by_id(self, order_id: int) -> Dict[str, Any]:
        """
        根据ID获取订单
        @param order_id: 订单ID
        @return: 订单数据
        """
        api_data = self._create_api_data(
            url=f"/orders/{order_id}",
            method="GET"
        )

        result = demo_project.order.get_order_by_id(api_data)
        if result.response and result.response.json().get("code") == 200:
            return result.response.json()["data"]
        return None

    def update(self, order_id: int, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新订单信息
        @param order_id: 订单ID
        @param order_data: 订单数据
        @return: 更新后的订单数据
        """
        api_data = self._create_api_data(
            url="/orders",
            method="PUT",
            params={"id": order_id},
            json_data=order_data
        )

        result = demo_project.order.update_order_info(api_data)
        if result.response and result.response.json().get("code") == 200:
            return result.response.json()["data"]
        return None

    def delete(self, order_id: int) -> bool:
        """
        删除订单
        @param order_id: 订单ID
        @return: 是否删除成功
        """
        api_data = self._create_api_data(
            url="/orders",
            method="DELETE",
            params={"id": order_id}
        )

        result = demo_project.order.delete_order(api_data)
        if result.response and result.response.json().get("code") == 200:
            return True
        return False

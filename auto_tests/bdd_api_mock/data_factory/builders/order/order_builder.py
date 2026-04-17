# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 订单构造器 - 对应 /orders 接口
# @Time   : 2026-03-31
# @Author : 毛鹏
from typing import Dict, Any, List

from auto_tests.bdd_api_mock.api_manager import bdd_api_mock
from core.base import BaseBuilder
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
            bdd_api_mock.order.set_token(token)
        self._created = []

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

        result = bdd_api_mock.order.create_order(
            product_id=order_data["product_id"],
            quantity=order_data["quantity"],
            user_id=order_data["user_id"]
        )

        if result.get("code") == 200:
            created_order = result["data"]
            self._created.append(created_order)
            return created_order
        return None

    def create_paid(self, product_id: int = None, quantity: int = None,
                    user_id: int = None) -> Dict[str, Any]:
        """
        创建已支付订单
        @return: 已支付订单数据
        """
        order = self.create(product_id, quantity, user_id)
        if order:
            order["status"] = "paid"
            self.update(order.get("id", 0), {"status": "paid"})
            order["status"] = "paid"
        return order

    def create_with_product(self, product_id: int, quantity: int = None,
                            user_id: int = None) -> Dict[str, Any]:
        """
        创建包含指定产品的订单
        @param product_id: 产品ID
        @param quantity: 数量
        @param user_id: 用户ID
        @return: 订单数据
        """
        return self.create(product_id, quantity, user_id)

    def create_batch(self, count: int = 5) -> list:
        """
        批量创建订单
        @param count: 数量
        @return: 创建的订单列表
        """
        results = []
        for i in range(count):
            order = self.create(product_id=1, quantity=i + 1, user_id=1)
            if order:
                results.append(order)
        return results

    def get_all(self) -> List[Dict[str, Any]]:
        """
        获取所有订单
        @return: 订单列表
        """
        result = bdd_api_mock.order.get_all_orders()
        if result.get("code") == 200:
            return result["data"]
        return []

    def get_by_id(self, order_id: int) -> Dict[str, Any]:
        """
        根据ID获取订单
        @param order_id: 订单ID
        @return: 订单数据
        """
        result = bdd_api_mock.order.get_order_by_id(order_id)
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
        result = bdd_api_mock.order.update_order_info(
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
        result = bdd_api_mock.order.delete_order(order_id)
        if result.get("code") == 200:
            return True
        return False

    def cleanup(self):
        """
        清理创建的数据
        """
        self._created.clear()

# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 批量订单场景
# @Time   : 2026-03-31
# @Author : 毛鹏
from typing import Dict, Any

from .base_scenario import BaseScenario
from ..builders.order import OrderBuilder
from ..builders.product import ProductBuilder
from ..builders.user import UserBuilder


class BatchOrderScenario(BaseScenario):
    """
    批量订单场景
    一个用户 + 多个产品 + 多个订单
    """

    def setup(self, product_count: int = 3, order_per_product: int = 2,
              **kwargs) -> Dict[str, Any]:
        """
        设置场景
        @param product_count: 产品数量
        @param order_per_product: 每个产品的订单数
        @return: 场景数据
        """
        # 创建用户
        user_builder = UserBuilder(self.token, self.factory)
        user = user_builder.create()
        self._record('user', user)

        # 创建产品
        product_builder = ProductBuilder(self.token, self.factory)
        products = product_builder.create_batch(product_count)
        for product in products:
            self._record('product', product)

        # 创建订单
        order_builder = OrderBuilder(self.token, self.factory)
        orders = []
        for product in products:
            for i in range(order_per_product):
                order = order_builder.create(
                    product_id=product.get('id'),
                    quantity=i + 1,
                    user_id=user.get('id')
                )
                if order:
                    orders.append(order)
                    self._record('order', order)

        return {
            'user': user,
            'products': products,
            'orders': orders,
            'total_orders': len(orders)
        }

    def teardown(self):
        """清理场景数据"""
        order_builder = OrderBuilder(self.token, self.factory)
        for order in self._created_data.get('order', []):
            try:
                order_builder.delete(order.get('id'))
            except Exception:
                pass

        product_builder = ProductBuilder(self.token, self.factory)
        for product in self._created_data.get('product', []):
            try:
                product_builder.delete(product.get('id'))
            except Exception:
                pass

        user_builder = UserBuilder(self.token, self.factory)
        for user in self._created_data.get('user', []):
            try:
                user_builder.delete(user.get('id'))
            except Exception:
                pass

        self._created_data.clear()

# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 简单订单场景
# @Time   : 2026-03-31
# @Author : 毛鹏
from typing import Dict, Any

from .base_scenario import BaseScenario
from ..builders.b_module.order_builder import OrderBuilder
from ..builders.c_module.product_builder import ProductBuilder
from ..builders.d_module.user_builder import UserBuilder


class SimpleOrderScenario(BaseScenario):
    """
    简单订单场景
    创建一个用户 + 一个产品 + 一个订单
    """

    def setup(self, quantity: int = 1, **kwargs) -> Dict[str, Any]:
        """
        设置场景
        @param quantity: 订单数量
        @return: 场景数据
        """
        # 创建用户
        user_builder = UserBuilder(self.token, self.factory)
        user = user_builder.create()
        self._record('user', user)

        # 创建产品
        product_builder = ProductBuilder(self.token, self.factory)
        product = product_builder.create()
        self._record('product', product)

        # 创建订单
        order_builder = OrderBuilder(self.token, self.factory)
        order = order_builder.create(
            product_id=product.get('id'),
            quantity=quantity,
            user_id=user.get('id')
        )
        self._record('order', order)

        return {
            'user': user,
            'product': product,
            'order': order
        }

    def teardown(self):
        """清理场景数据"""
        # 按依赖顺序清理：先删订单，再删产品，最后删用户
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

# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 复杂工作流场景
# @Time   : 2026-03-31
# @Author : 毛鹏
from typing import Dict, Any

from .base_scenario import BaseScenario
from ..builders.a_module.data_builder import DataBuilder
from ..builders.b_module.order_builder import OrderBuilder
from ..builders.c_module.product_builder import ProductBuilder
from ..builders.d_module.user_builder import UserBuilder


class ComplexWorkflowScenario(BaseScenario):
    """
    复杂工作流场景
    多用户 + 多产品 + 多订单 + 数据提交
    模拟完整的业务流程
    """

    def setup(self, user_count: int = 2, product_count: int = 3,
              orders_per_user: int = 2, **kwargs) -> Dict[str, Any]:
        """
        设置复杂场景
        @param user_count: 用户数量
        @param product_count: 产品数量
        @param orders_per_user: 每个用户的订单数
        @return: 场景数据
        """
        user_builder = UserBuilder(self.token, self.factory)
        product_builder = ProductBuilder(self.token, self.factory)
        order_builder = OrderBuilder(self.token, self.factory)
        data_builder = DataBuilder(self.token, self.factory)

        # 创建多个用户
        users = []
        for i in range(user_count):
            user = user_builder.create()
            users.append(user)
            self._record('user', user)

        # 创建多个产品
        products = product_builder.create_batch(product_count)
        for product in products:
            self._record('product', product)

        # 为每个用户创建订单
        orders = []
        for user in users:
            for i in range(orders_per_user):
                product = products[i % len(products)]
                order = order_builder.create(
                    product_id=product.get('id'),
                    quantity=i + 1,
                    user_id=user.get('id')
                )
                if order:
                    orders.append(order)
                    self._record('order', order)

        # 提交业务数据
        data_items = []
        for i, order in enumerate(orders):
            data = data_builder.create(
                name=f"order_data_{order.get('id')}",
                value=order.get('quantity', 1) * 100
            )
            if data:
                data_items.append(data)
                self._record('data', data)

        return {
            'users': users,
            'products': products,
            'orders': orders,
            'data_items': data_items,
            'summary': {
                'user_count': len(users),
                'product_count': len(products),
                'order_count': len(orders),
                'data_count': len(data_items)
            }
        }

    def teardown(self):
        """清理场景数据"""
        # 注意：data接口可能没有删除功能，所以只清理其他数据
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

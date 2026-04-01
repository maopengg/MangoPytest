# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 订单管理测试用例 - /orders
# @Time   : 2026-03-31
# @Author : 毛鹏
import pytest
import allure

from auto_test.demo_project.data_factory.builders.auth import AuthBuilder
from auto_test.demo_project.data_factory.builders.product import ProductBuilder
from auto_test.demo_project.data_factory.builders.order import OrderBuilder
from auto_test.demo_project.data_factory.builders.user import UserBuilder
from auto_test.demo_project.fixtures.conftest import *


@allure.feature("订单管理")
@allure.story("创建订单")
class TestCreateOrder:
    """创建订单接口测试"""

    @allure.title("正常创建订单")
    def test_create_order_success(self, test_token):
        """测试正常创建订单"""
        # 先创建产品和获取用户
        product_builder = ProductBuilder(token=test_token)
        product = product_builder.create()
        assert product is not None
        
        user_builder = UserBuilder(token=test_token)
        users = user_builder.get_all()
        assert len(users) > 0
        user_id = users[0].id
        
        # 创建订单
        order_builder = OrderBuilder(token=test_token)
        order = order_builder.create(
            product_id=product.get('id'),
            user_id=user_id,
            quantity=2
        )
        
        assert order is not None
        assert order.get('id') is not None
        assert order.get('product_id') == product.get('id')
        assert order.get('user_id') == user_id
        assert order.get('quantity') == 2
        
        # 清理
        order_builder.delete(order.get('id'))
        product_builder.delete(product.get('id'))

    @allure.title("创建订单-使用fixture数据")
    def test_create_order_with_fixture(self, test_token, test_product, test_user):
        """测试使用fixture创建的数据创建订单"""
        order_builder = OrderBuilder(token=test_token)
        order = order_builder.create(
            product_id=test_product.get('id'),
            user_id=test_user.id,
            quantity=5
        )
        
        assert order is not None
        assert order.get('product_id') == test_product.get('id')
        assert order.get('user_id') == test_user.id
        assert order.get('quantity') == 5
        
        # 清理
        order_builder.delete(order.get('id'))

    @allure.title("创建订单-数量为1")
    def test_create_order_quantity_one(self, test_token):
        """测试创建数量为1的订单"""
        product_builder = ProductBuilder(token=test_token)
        product = product_builder.create()
        assert product is not None
        
        user_builder = UserBuilder(token=test_token)
        users = user_builder.get_all()
        user_id = users[0].id
        
        order_builder = OrderBuilder(token=test_token)
        order = order_builder.create(
            product_id=product.get('id'),
            user_id=user_id,
            quantity=1
        )
        
        assert order is not None
        assert order.get('quantity') == 1
        
        # 清理
        order_builder.delete(order.get('id'))
        product_builder.delete(product.get('id'))


@allure.feature("订单管理")
@allure.story("获取订单")
class TestGetOrders:
    """获取订单接口测试"""

    @allure.title("获取所有订单")
    def test_get_all_orders(self, test_token):
        """测试获取所有订单列表"""
        order_builder = OrderBuilder(token=test_token)
        
        # 先创建几个订单
        product_builder = ProductBuilder(token=test_token)
        product1 = product_builder.create()
        product2 = product_builder.create()
        
        user_builder = UserBuilder(token=test_token)
        users = user_builder.get_all()
        user_id = users[0].id
        
        order1 = order_builder.create(product_id=product1.get('id'), user_id=user_id, quantity=1)
        order2 = order_builder.create(product_id=product2.get('id'), user_id=user_id, quantity=2)
        
        # 获取所有订单
        orders = order_builder.get_all()
        
        assert isinstance(orders, list)
        assert len(orders) >= 2
        
        # 清理
        order_builder.delete(order1.get('id'))
        order_builder.delete(order2.get('id'))
        product_builder.delete(product1.get('id'))
        product_builder.delete(product2.get('id'))

    @allure.title("根据ID获取订单")
    def test_get_order_by_id(self, test_token):
        """测试根据ID获取订单"""
        # 先创建一个订单
        product_builder = ProductBuilder(token=test_token)
        product = product_builder.create()
        
        user_builder = UserBuilder(token=test_token)
        users = user_builder.get_all()
        user_id = users[0].id
        
        order_builder = OrderBuilder(token=test_token)
        order = order_builder.create(
            product_id=product.get('id'),
            user_id=user_id,
            quantity=3
        )
        assert order is not None
        
        # 根据ID获取
        fetched_order = order_builder.get_by_id(order.get('id'))
        
        assert fetched_order is not None
        assert fetched_order.get('id') == order.get('id')
        assert fetched_order.get('quantity') == 3
        
        # 清理
        order_builder.delete(order.get('id'))
        product_builder.delete(product.get('id'))

    @allure.title("获取不存在的订单")
    def test_get_nonexistent_order(self, test_token):
        """测试获取不存在的订单"""
        order_builder = OrderBuilder(token=test_token)
        order = order_builder.get_by_id(99999)
        
        assert order is None


@allure.feature("订单管理")
@allure.story("更新订单")
class TestUpdateOrder:
    """更新订单接口测试"""

    @allure.title("正常更新订单")
    def test_update_order_success(self, test_token):
        """测试正常更新订单"""
        # 先创建一个订单
        product_builder = ProductBuilder(token=test_token)
        product = product_builder.create()
        
        user_builder = UserBuilder(token=test_token)
        users = user_builder.get_all()
        user_id = users[0].id
        
        order_builder = OrderBuilder(token=test_token)
        order = order_builder.create(
            product_id=product.get('id'),
            user_id=user_id,
            quantity=1
        )
        assert order is not None
        
        # 更新订单
        update_data = {
            "id": order.get('id'),
            "product_id": product.get('id'),
            "user_id": user_id,
            "quantity": 10
        }
        updated_order = order_builder.update(order.get('id'), update_data)
        
        assert updated_order is not None
        assert updated_order.get('quantity') == 10
        
        # 清理
        order_builder.delete(order.get('id'))
        product_builder.delete(product.get('id'))

    @allure.title("更新不存在的订单")
    def test_update_nonexistent_order(self, test_token):
        """测试更新不存在的订单"""
        order_builder = OrderBuilder(token=test_token)
        
        update_data = {
            "id": 99999,
            "product_id": 1,
            "user_id": 1,
            "quantity": 5
        }
        result = order_builder.update(99999, update_data)
        
        assert result is None


@allure.feature("订单管理")
@allure.story("删除订单")
class TestDeleteOrder:
    """删除订单接口测试"""

    @allure.title("正常删除订单")
    def test_delete_order_success(self, test_token):
        """测试正常删除订单"""
        # 先创建一个订单
        product_builder = ProductBuilder(token=test_token)
        product = product_builder.create()
        
        user_builder = UserBuilder(token=test_token)
        users = user_builder.get_all()
        user_id = users[0].id
        
        order_builder = OrderBuilder(token=test_token)
        order = order_builder.create(
            product_id=product.get('id'),
            user_id=user_id,
            quantity=1
        )
        assert order is not None
        order_id = order.get('id')
        
        # 删除订单
        result = order_builder.delete(order_id)
        
        assert result is True
        
        # 验证订单已被删除
        deleted_order = order_builder.get_by_id(order_id)
        assert deleted_order is None
        
        # 清理产品
        product_builder.delete(product.get('id'))

    @allure.title("删除不存在的订单")
    def test_delete_nonexistent_order(self, test_token):
        """测试删除不存在的订单"""
        order_builder = OrderBuilder(token=test_token)
        result = order_builder.delete(99999)
        
        assert result is False

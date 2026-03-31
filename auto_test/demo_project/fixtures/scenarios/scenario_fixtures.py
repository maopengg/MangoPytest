# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 场景fixtures - 基于 mock_api 接口
# @Time   : 2026-03-31
# @Author : 毛鹏
import pytest
from typing import Generator, Dict, Any

from auto_test.demo_project.data_factory.builders.auth import AuthBuilder
from auto_test.demo_project.data_factory.builders.user import UserBuilder
from auto_test.demo_project.data_factory.builders.product import ProductBuilder
from auto_test.demo_project.data_factory.builders.order import OrderBuilder


@pytest.fixture(scope="function")
def user_with_order(test_token) -> Generator[Dict[str, Any], None, None]:
    """
    用户带订单场景
    创建一个用户、一个产品和一个订单
    """
    auth_builder = AuthBuilder(token=test_token)
    product_builder = ProductBuilder(token=test_token)
    order_builder = OrderBuilder(token=test_token)
    
    # 注册用户
    user = auth_builder.register()
    if not user:
        pytest.skip("无法创建测试用户")
    
    # 创建产品
    product = product_builder.create()
    if not product:
        pytest.skip("无法创建测试产品")
    
    # 创建订单
    order = order_builder.create(
        product_id=product.get('id'),
        user_id=user.get('id'),
        quantity=1
    )
    if not order:
        # 清理
        try:
            product_builder.delete(product.get('id'))
        except Exception:
            pass
        pytest.skip("无法创建测试订单")
    
    yield {
        "user": user,
        "product": product,
        "order": order
    }
    
    # 清理
    try:
        order_builder.delete(order.get('id'))
        product_builder.delete(product.get('id'))
    except Exception:
        pass


@pytest.fixture(scope="function")
def multiple_orders(test_token) -> Generator[Dict[str, Any], None, None]:
    """
    多订单场景
    创建一个用户、多个产品和多个订单
    """
    auth_builder = AuthBuilder(token=test_token)
    product_builder = ProductBuilder(token=test_token)
    order_builder = OrderBuilder(token=test_token)
    
    # 注册用户
    user = auth_builder.register()
    if not user:
        pytest.skip("无法创建测试用户")
    
    # 创建多个产品
    products = []
    orders = []
    
    for i in range(3):
        product = product_builder.create()
        if product:
            products.append(product)
            # 为每个产品创建订单
            order = order_builder.create(
                product_id=product.get('id'),
                user_id=user.get('id'),
                quantity=i + 1
            )
            if order:
                orders.append(order)
    
    if not products or not orders:
        # 清理
        for order in orders:
            try:
                order_builder.delete(order.get('id'))
            except Exception:
                pass
        for product in products:
            try:
                product_builder.delete(product.get('id'))
            except Exception:
                pass
        pytest.skip("无法创建足够的测试数据")
    
    yield {
        "user": user,
        "products": products,
        "orders": orders
    }
    
    # 清理
    for order in orders:
        try:
            order_builder.delete(order.get('id'))
        except Exception:
            pass
    for product in products:
        try:
            product_builder.delete(product.get('id'))
        except Exception:
            pass


@pytest.fixture(scope="function")
def complete_workflow(test_token) -> Generator[Dict[str, Any], None, None]:
    """
    完整工作流场景
    包含：登录、获取用户列表、创建产品、创建订单、查询订单
    """
    auth_builder = AuthBuilder(token=test_token)
    user_builder = UserBuilder(token=test_token)
    product_builder = ProductBuilder(token=test_token)
    order_builder = OrderBuilder(token=test_token)
    
    # 登录获取token
    token = auth_builder.login()
    if not token:
        pytest.skip("无法登录")
    
    # 更新token
    user_builder.set_token(token)
    product_builder.set_token(token)
    order_builder.set_token(token)
    
    # 获取用户列表
    users = user_builder.get_all()
    if not users:
        pytest.skip("无法获取用户列表")
    
    user = users[0]
    
    # 创建产品
    product = product_builder.create()
    if not product:
        pytest.skip("无法创建产品")
    
    # 创建订单
    order = order_builder.create(
        product_id=product.get('id'),
        user_id=user.get('id'),
        quantity=2
    )
    if not order:
        try:
            product_builder.delete(product.get('id'))
        except Exception:
            pass
        pytest.skip("无法创建订单")
    
    # 查询订单详情
    order_detail = order_builder.get_by_id(order.get('id'))
    
    yield {
        "token": token,
        "user": user,
        "product": product,
        "order": order,
        "order_detail": order_detail
    }
    
    # 清理
    try:
        order_builder.delete(order.get('id'))
        product_builder.delete(product.get('id'))
    except Exception:
        pass

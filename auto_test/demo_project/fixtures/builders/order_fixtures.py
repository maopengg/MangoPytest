# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 订单模块 fixtures
# @Time   : 2026-03-31
# @Author : 毛鹏
import pytest
from typing import Generator, Dict, Any

from auto_test.demo_project.data_factory.builders.order import OrderBuilder
from auto_test.demo_project.data_factory.builders.product import ProductBuilder


@pytest.fixture(scope="function")
def order_builder(test_token) -> OrderBuilder:
    """订单构造器 fixture"""
    return OrderBuilder(token=test_token)


@pytest.fixture(scope="function")
def test_order(order_builder, test_product, test_user) -> Generator[Dict[str, Any], None, None]:
    """
    测试订单 fixture
    创建一个新的测试订单
    """
    order = order_builder.create(
        product_id=test_product.get('id'),
        user_id=test_user.get('id'),
        quantity=1
    )
    if not order:
        pytest.skip("无法创建测试订单")
    
    yield order
    
    # 清理
    try:
        order_builder.delete(order.get('id'))
    except Exception:
        pass


@pytest.fixture(scope="function")
def order_with_product(order_builder, product_builder, test_user) -> Generator[Dict[str, Any], None, None]:
    """
    带产品的订单 fixture
    自动创建产品并下单
    """
    # 先创建产品
    product = product_builder.create()
    if not product:
        pytest.skip("无法创建测试产品")

    # 创建订单
    order = order_builder.create(
        product_id=product.get('id'),
        user_id=test_user.get('id'),
        quantity=2
    )
    if not order:
        # 清理产品
        try:
            product_builder.delete(product.get('id'))
        except Exception:
            pass
        pytest.skip("无法创建测试订单")

    yield order

    # 清理
    try:
        order_builder.delete(order.get('id'))
        product_builder.delete(product.get('id'))
    except Exception:
        pass

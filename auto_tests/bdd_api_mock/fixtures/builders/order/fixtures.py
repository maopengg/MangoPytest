# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 订单模块 fixtures
# @Time   : 2026-03-31
# @Author : 毛鹏
from typing import Generator, Dict, Any

import pytest

from auto_tests.bdd_api_mock.data_factory.builders.order import OrderBuilder


@pytest.fixture(scope="function")
def order_builder(authenticated_client) -> Generator[OrderBuilder, None, None]:
    """
    订单构造器 fixture
    提供OrderBuilder实例用于创建和管理订单
    """
    builder = OrderBuilder(token=authenticated_client.token)
    yield builder
    # 清理创建的数据
    builder.cleanup()


@pytest.fixture
def test_order(order_builder) -> Dict[str, Any]:
    """
    测试订单 fixture
    创建一个测试订单
    """
    order = order_builder.create()
    return order


@pytest.fixture
def order_list(order_builder) -> list:
    """
    订单列表 fixture
    创建多个测试订单
    """
    orders = order_builder.create_batch(5)
    return orders


@pytest.fixture
def paid_order(order_builder) -> Dict[str, Any]:
    """
    已支付订单 fixture
    创建一个已支付的订单
    """
    order = order_builder.create_paid()
    return order


@pytest.fixture
def order_with_product(order_builder, test_product) -> Dict[str, Any]:
    """
    带产品的订单 fixture
    创建一个包含指定产品的订单
    """
    product_id = test_product.get("id") if isinstance(test_product, dict) else test_product.id
    order = order_builder.create_with_product(product_id)
    return order

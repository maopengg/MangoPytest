# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 产品模块 fixtures
# @Time   : 2026-03-31
# @Author : 毛鹏
from typing import Generator, Dict, Any

import pytest

from auto_tests.bdd_api_mock.data_factory.builders.product import ProductBuilder


@pytest.fixture(scope="function")
def product_builder(authenticated_client) -> Generator[ProductBuilder, None, None]:
    """
    产品构造器 fixture
    提供ProductBuilder实例用于创建和管理产品
    """
    builder = ProductBuilder(token=authenticated_client.token)
    yield builder
    # 清理创建的数据
    builder.cleanup()


@pytest.fixture
def test_product(product_builder) -> Dict[str, Any]:
    """
    测试产品 fixture
    创建一个测试产品
    """
    product = product_builder.create()
    return product


@pytest.fixture
def product_list(product_builder) -> list:
    """
    产品列表 fixture
    创建多个测试产品
    """
    products = product_builder.create_batch(5)
    return products


@pytest.fixture
def out_of_stock_product(product_builder) -> Dict[str, Any]:
    """
    缺货产品 fixture
    创建一个库存为0的产品
    """
    product = product_builder.create_out_of_stock()
    return product

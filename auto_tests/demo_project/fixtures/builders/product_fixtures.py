# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 产品模块 fixtures
# @Time   : 2026-03-31
# @Author : 毛鹏
from typing import Generator, Dict, Any

import pytest

from auto_tests.demo_project.data_factory.builders.product import ProductBuilder


@pytest.fixture(scope="function")
def product_builder(test_token) -> ProductBuilder:
    """产品构造器 fixture"""
    return ProductBuilder(token=test_token)


@pytest.fixture(scope="function")
def test_product(product_builder) -> Generator[Dict[str, Any], None, None]:
    """
    测试产品 fixture
    创建一个新的测试产品
    """
    product = product_builder.create()
    if not product:
        pytest.skip("无法创建测试产品")

    yield product

    # 清理
    try:
        product_builder.delete(product.get('id'))
    except Exception:
        pass


@pytest.fixture(scope="function")
def product_list(product_builder) -> Generator[list, None, None]:
    """
    产品列表 fixture
    获取所有产品列表
    """
    products = product_builder.get_all()
    yield products

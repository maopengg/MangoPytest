# -*- coding: utf-8 -*-
"""
产品 Spec - pytest-factoryboy
使用 AUTO_ 前缀，便于自动清理
"""

import factory
from pytest_factoryboy import register
from datetime import datetime
from decimal import Decimal

from core.base.base_factory import BaseFactory
from auto_tests.bdd_api_mock.data_factory.entities.product.product_entity import ProductEntity

# 使用 mangotools.data_processor 生成测试数据
from mangotools.data_processor import DataProcessor

_data_processor = DataProcessor()


def auto_product_name():
    """生成 AUTO_ 前缀的产品名"""
    unique_id = _data_processor.str_uuid_no_dash()[:8]
    return f"AUTO_PRODUCT_{unique_id}"


@register
class ProductSpec(BaseFactory):
    """产品 Spec"""

    class Meta:
        model = ProductEntity

    # 基本字段 - 使用 AUTO_ 前缀
    name = factory.LazyFunction(auto_product_name)
    price = factory.LazyFunction(
        lambda: Decimal(str(__import__("random").uniform(10, 10000))).quantize(
            Decimal("0.01")
        )
    )
    description = factory.LazyAttribute(lambda o: f"这是 {o.name} 的描述")
    stock = factory.LazyFunction(lambda: __import__("random").randint(0, 1000))
    category = factory.Iterator(
        ["electronics", "accessories", "audio", "storage", "office"]
    )
    status = "active"
    created_at = factory.LazyFunction(datetime.now)
    updated_at = factory.LazyFunction(datetime.now)

    # Trait: 不同状态
    class Params:
        out_of_stock = factory.Trait(
            stock=0,
        )
        inactive = factory.Trait(
            status="inactive",
        )

# -*- coding: utf-8 -*-
"""
产品 Spec - pytest-factoryboy
使用 AUTO_ 前缀，便于自动清理
"""

import factory
from pytest_factoryboy import register
from datetime import datetime
from decimal import Decimal

from auto_tests.bdd_api_mock.factories import BaseFactory
from auto_tests.bdd_api_mock.factories.utils import auto_product_name
from auto_tests.bdd_api_mock.entities.product.product_entity import ProductEntity


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

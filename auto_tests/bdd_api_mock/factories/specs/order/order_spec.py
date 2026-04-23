# -*- coding: utf-8 -*-
"""
订单 Spec - pytest-factoryboy
使用 AUTO_ 前缀，便于自动清理
"""

import factory
from pytest_factoryboy import register
from datetime import datetime
from decimal import Decimal

from auto_tests.bdd_api_mock.factories import BaseFactory
from auto_tests.bdd_api_mock.factories.specs.user.user_spec import UserSpec
from auto_tests.bdd_api_mock.factories.specs.product.product_spec import ProductSpec
from auto_tests.bdd_api_mock.factories.utils import auto_order_no
from auto_tests.bdd_api_mock.entities.order.order_entity import OrderEntity


@register
class OrderSpec(BaseFactory):
    """订单 Spec"""

    class Meta:
        model = OrderEntity
        exclude = ("_user", "_product")

    # 关联实体 - 自动创建
    _user = factory.SubFactory(UserSpec)
    _product = factory.SubFactory(ProductSpec)

    # 外键字段
    user_id = factory.SelfAttribute("_user.id")
    product_id = factory.SelfAttribute("_product.id")

    # 基本字段 - 使用 AUTO_ 前缀
    order_no = factory.LazyFunction(auto_order_no)
    quantity = 1
    unit_price = factory.SelfAttribute("_product.price")
    total_amount = factory.LazyAttribute(
        lambda o: Decimal(str(o.unit_price)) * o.quantity
    )
    status = "pending"
    remark = None
    created_at = factory.LazyFunction(datetime.now)
    updated_at = factory.LazyFunction(datetime.now)

    # Trait: 不同状态
    class Params:
        paid = factory.Trait(
            status="paid",
        )
        shipped = factory.Trait(
            status="shipped",
        )
        completed = factory.Trait(
            status="completed",
        )

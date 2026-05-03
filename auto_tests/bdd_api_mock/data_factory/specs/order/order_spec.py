# -*- coding: utf-8 -*-
"""
订单 Spec - pytest-factoryboy
使用 AUTO_ 前缀，便于自动清理
"""

import factory
from pytest_factoryboy import register
from datetime import datetime
from decimal import Decimal

from core.base.base_factory import BaseFactory
from auto_tests.bdd_api_mock.data_factory.specs.user.user_spec import UserSpec
from auto_tests.bdd_api_mock.data_factory.specs.product.product_spec import ProductSpec
from auto_tests.bdd_api_mock.data_factory.entities.order.order_entity import OrderEntity

# 使用 mangotools.data_processor 生成测试数据
from mangotools.data_processor import DataProcessor

_data_processor = DataProcessor()


def auto_order_no():
    """生成 AUTO_ 前缀的订单号"""
    unique_id = _data_processor.str_uuid_no_dash()[:8]
    return f"AUTO_ORDER_{unique_id}"


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

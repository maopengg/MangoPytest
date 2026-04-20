# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 订单管理模块 BDD 步骤定义
# @Time   : 2026-04-17
# @Author : 毛鹏
"""
订单管理模块步骤定义
"""

import pytest
from pytest_bdd import given, when, then, parsers
from pytest_bdd.parsers import parse

from auto_tests.bdd_api_mock.data_factory.builders.order import OrderBuilder
from auto_tests.bdd_api_mock.data_factory.builders.product import ProductBuilder
from auto_tests.bdd_api_mock.data_factory.builders.user import UserBuilder
from auto_tests.bdd_api_mock.api_manager import bdd_api_mock


# ==================== Given 步骤 ====================


@given("系统中存在可用的产品", target_fixture="available_product")
def prepare_available_product(authenticated_user):
    """准备可用产品"""
    token = authenticated_user["token"]
    product_builder = ProductBuilder(token=token)
    products = product_builder.get_all()
    if len(products) == 0:
        product = product_builder.create(name="Test Product", price=99.99)
        return product
    return products[0]


@given("用户选择了产品", target_fixture="selected_product")
def user_selected_product(available_product):
    """用户选择产品"""
    return available_product


@given("用户已创建测试订单", target_fixture="test_order")
def prepare_test_order(authenticated_user, selected_product):
    """准备测试订单"""
    token = authenticated_user["token"]
    order_builder = OrderBuilder(token=token)

    # 获取用户ID
    user_builder = UserBuilder(token=token)
    users = user_builder.get_all()
    user_id = users[0]["id"] if users else 1

    product_id = (
        selected_product.get("id")
        if isinstance(selected_product, dict)
        else selected_product.id
    )

    order = order_builder.create(product_id=product_id, user_id=user_id, quantity=2)
    return order


# ==================== When 步骤 ====================


@when(
    parsers.parse("用户创建订单，数量为 {quantity:d}"), target_fixture="created_order"
)
def user_create_order(authenticated_user, selected_product, quantity):
    """用户创建订单"""
    token = authenticated_user["token"]
    order_builder = OrderBuilder(token=token)

    # 获取用户ID
    user_builder = UserBuilder(token=token)
    users = user_builder.get_all()
    user_id = users[0]["id"] if users else 1

    product_id = (
        selected_product.get("id")
        if isinstance(selected_product, dict)
        else selected_product.id
    )

    order = order_builder.create(
        product_id=product_id, user_id=user_id, quantity=quantity
    )
    return order


@when("用户批量创建 3 个订单", target_fixture="created_orders")
def user_create_multiple_orders(authenticated_user, selected_product):
    """用户批量创建订单"""
    token = authenticated_user["token"]
    order_builder = OrderBuilder(token=token)

    # 获取用户ID
    user_builder = UserBuilder(token=token)
    users = user_builder.get_all()
    user_id = users[0]["id"] if users else 1

    product_id = (
        selected_product.get("id")
        if isinstance(selected_product, dict)
        else selected_product.id
    )

    orders = []
    for i in range(3):
        order = order_builder.create(
            product_id=product_id, user_id=user_id, quantity=i + 1
        )
        orders.append(order)
    return orders


@when("用户请求获取所有订单", target_fixture="orders_list")
def user_get_all_orders(authenticated_user):
    """用户获取所有订单"""
    token = authenticated_user["token"]
    order_builder = OrderBuilder(token=token)
    orders = order_builder.get_all()
    return orders


@when("用户根据该订单ID查询订单信息", target_fixture="fetched_order")
def user_get_order_by_id(authenticated_user, test_order):
    """用户根据ID获取订单"""
    token = authenticated_user["token"]
    order_builder = OrderBuilder(token=token)
    order_id = test_order.get("id") if isinstance(test_order, dict) else test_order.id
    order = order_builder.get_by_id(order_id)
    return order


# ==================== Then 步骤 ====================


@then("订单应该创建成功")
def verify_order_created(created_order):
    """验证订单创建成功"""
    assert created_order is not None


@then("订单应该包含有效的订单ID")
def verify_order_has_id(created_order):
    """验证订单包含有效ID"""
    order_id = (
        created_order.get("id") if isinstance(created_order, dict) else created_order.id
    )
    assert order_id is not None


@then("订单中的产品ID应该匹配")
def verify_order_product_id_matches(created_order, selected_product):
    """验证订单产品ID匹配"""
    expected_id = (
        selected_product.get("id")
        if isinstance(selected_product, dict)
        else selected_product.id
    )
    actual_id = (
        created_order.get("product_id")
        if isinstance(created_order, dict)
        else created_order.product_id
    )
    assert actual_id == expected_id


@then(parsers.parse("订单数量应该是 {quantity:d}"))
def verify_order_quantity(created_order, quantity):
    """验证订单数量"""
    order_quantity = (
        created_order.get("quantity")
        if isinstance(created_order, dict)
        else created_order.quantity
    )
    assert order_quantity == quantity


@then("所有订单都应该创建成功")
def verify_all_orders_created(created_orders):
    """验证所有订单都创建成功"""
    for order in created_orders:
        assert order is not None


@then(parsers.parse("总共应该创建 {count:d} 个订单"))
def verify_orders_count(created_orders, count):
    """验证创建的订单数量"""
    assert len(created_orders) == count


@then("应该成功返回订单列表")
def verify_orders_list_returned(orders_list):
    """验证成功返回订单列表"""
    assert isinstance(orders_list, list)


@then("应该成功返回该订单信息")
def verify_order_returned(fetched_order):
    """验证成功返回订单信息"""
    assert fetched_order is not None


@then("返回的订单ID应该匹配")
def verify_order_id_matches(fetched_order, test_order):
    """验证返回的订单ID匹配"""
    expected_id = (
        test_order.get("id") if isinstance(test_order, dict) else test_order.id
    )
    actual_id = (
        fetched_order.get("id") if isinstance(fetched_order, dict) else fetched_order.id
    )
    assert actual_id == expected_id

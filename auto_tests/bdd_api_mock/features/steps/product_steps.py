# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 产品管理模块 BDD 步骤定义
# @Time   : 2026-04-17
# @Author : 毛鹏
"""
产品管理模块步骤定义
"""

import pytest
from pytest_bdd import given, when, then, parsers
from pytest_bdd.parsers import parse

from auto_tests.bdd_api_mock.data_factory.builders.product import ProductBuilder
from auto_tests.bdd_api_mock.api_manager import bdd_api_mock


# ==================== Given 步骤 ====================


@given("系统中存在测试产品", target_fixture="test_product")
def prepare_test_product(admin_user_logged_in):
    """准备测试产品"""
    token = admin_user_logged_in["token"]
    product_builder = ProductBuilder(token=token)
    products = product_builder.get_all()
    if len(products) == 0:
        # 如果没有产品，创建一个
        product = product_builder.create(name="Test Product", price=99.99)
        return product
    return products[0]


# ==================== When 步骤 ====================


@when("管理员创建新产品，数据如下:", target_fixture="created_product")
def admin_create_product_with_data(admin_user_logged_in, table):
    """管理员创建产品"""
    token = admin_user_logged_in["token"]
    product_builder = ProductBuilder(token=token)
    rows = list(table)
    product_data = {"name": rows[0]["name"], "price": float(rows[0]["price"])}
    if "description" in rows[0]:
        product_data["description"] = rows[0]["description"]
    if "stock" in rows[0]:
        product_data["stock"] = int(rows[0]["stock"])

    product = product_builder.create(**product_data)
    return product


@when("管理员创建新产品，仅提供必填字段:", target_fixture="created_product")
def admin_create_product_required_only(admin_user_logged_in, table):
    """管理员仅使用必填字段创建产品"""
    token = admin_user_logged_in["token"]
    product_builder = ProductBuilder(token=token)
    rows = list(table)
    product = product_builder.create(
        name=rows[0]["name"], price=float(rows[0]["price"])
    )
    return product


@when("管理员请求获取所有产品", target_fixture="products_list")
def admin_get_all_products(admin_user_logged_in):
    """管理员获取所有产品"""
    token = admin_user_logged_in["token"]
    product_builder = ProductBuilder(token=token)
    products = product_builder.get_all()
    return products


@when("管理员根据该产品ID查询产品信息", target_fixture="fetched_product")
def admin_get_product_by_id(admin_user_logged_in, test_product):
    """管理员根据ID获取产品"""
    token = admin_user_logged_in["token"]
    product_builder = ProductBuilder(token=token)
    product_id = (
        test_product.get("id") if isinstance(test_product, dict) else test_product.id
    )
    product = product_builder.get_by_id(product_id)
    return product


@when("管理员批量创建以下产品:", target_fixture="created_products")
def admin_create_multiple_products(admin_user_logged_in, table):
    """管理员批量创建产品"""
    token = admin_user_logged_in["token"]
    product_builder = ProductBuilder(token=token)
    products = []
    for row in table:
        product = product_builder.create(name=row["name"], price=float(row["price"]))
        products.append(product)
    return products


# ==================== Then 步骤 ====================


@then("产品应该创建成功")
def verify_product_created(created_product):
    """验证产品创建成功"""
    assert created_product is not None


@then("返回的产品应该包含有效的ID")
def verify_product_has_id(created_product):
    """验证产品包含有效ID"""
    product_id = (
        created_product.get("id")
        if isinstance(created_product, dict)
        else created_product.id
    )
    assert product_id is not None


@then(parsers.parse('产品名称应该是 "{name}"'))
def verify_product_name(created_product, name):
    """验证产品名称"""
    product_name = (
        created_product.get("name")
        if isinstance(created_product, dict)
        else created_product.name
    )
    assert product_name == name


@then(parsers.parse("产品价格应该是 {price:f}"))
def verify_product_price(created_product, price):
    """验证产品价格"""
    product_price = (
        created_product.get("price")
        if isinstance(created_product, dict)
        else created_product.price
    )
    assert product_price == price


@then("应该成功返回产品列表")
def verify_products_list_returned(products_list):
    """验证成功返回产品列表"""
    assert isinstance(products_list, list)


@then("产品列表应该是数组类型")
def verify_products_list_is_array(products_list):
    """验证产品列表是数组类型"""
    assert isinstance(products_list, list)


@then("应该成功返回该产品信息")
def verify_product_returned(fetched_product):
    """验证成功返回产品信息"""
    assert fetched_product is not None


@then("返回的产品ID应该匹配")
def verify_product_id_matches(fetched_product, test_product):
    """验证返回的产品ID匹配"""
    expected_id = (
        test_product.get("id") if isinstance(test_product, dict) else test_product.id
    )
    actual_id = (
        fetched_product.get("id")
        if isinstance(fetched_product, dict)
        else fetched_product.id
    )
    assert actual_id == expected_id


@then("所有产品都应该创建成功")
def verify_all_products_created(created_products):
    """验证所有产品都创建成功"""
    for product in created_products:
        assert product is not None


@then(parsers.parse("总共应该创建 {count:d} 个产品"))
def verify_products_count(created_products, count):
    """验证创建的产品数量"""
    assert len(created_products) == count

# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 数据管理模块 BDD 步骤定义
# @Time   : 2026-04-17
# @Author : 毛鹏
"""
数据管理模块步骤定义
"""

import pytest
from pytest_bdd import given, when, then, parsers
from pytest_bdd.parsers import parse

from auto_tests.bdd_api_mock.api_manager import bdd_api_mock


# ==================== Given 步骤 ====================


@given("系统已通过fixture提交数据", target_fixture="fixture_submitted_data")
def prepare_data_via_fixture():
    """通过fixture准备数据"""
    # 这里模拟fixture提交的数据
    return {"name": "test_data", "value": 100}


# ==================== When 步骤 ====================


@when("用户提交数据:", target_fixture="submit_result")
def user_submit_data(authenticated_user, table):
    """用户提交数据"""
    token = authenticated_user["token"]
    bdd_api_mock.data.set_token(token)

    rows = list(table)
    name = rows[0]["name"]
    value = int(rows[0]["value"])

    result = bdd_api_mock.data.submit_data(name=name, value=value)
    return result


@when(
    parsers.parse('用户提交名称为 "{name}" 的数据，值为 {value:d}'),
    target_fixture="submit_result",
)
def user_submit_data_with_params(authenticated_user, name, value):
    """用户提交指定名称和值的数据"""
    token = authenticated_user["token"]
    bdd_api_mock.data.set_token(token)

    result = bdd_api_mock.data.submit_data(name=name, value=value)
    return result


@when("用户提交名称为空的数据，值为 100", target_fixture="submit_result")
def user_submit_empty_name_data(authenticated_user):
    """用户提交空名称的数据"""
    token = authenticated_user["token"]
    bdd_api_mock.data.set_token(token)

    result = bdd_api_mock.data.submit_data(name="", value=100)
    return result


# ==================== Then 步骤 ====================


@then("数据应该提交成功")
def verify_data_submitted(submit_result):
    """验证数据提交成功"""
    assert submit_result.get("code") == 200


@then(parsers.parse('返回的数据名称应该是 "{name}"'))
def verify_submitted_data_name(submit_result, name):
    """验证返回的数据名称"""
    data = submit_result.get("data", {})
    assert data.get("name") == name


@then(parsers.parse("返回的数据值应该是 {value:d}"))
def verify_submitted_data_value(submit_result, value):
    """验证返回的数据值"""
    data = submit_result.get("data", {})
    assert data.get("value") == value


@then("数据提交应该失败")
def verify_data_submit_failed(submit_result):
    """验证数据提交失败"""
    assert submit_result.get("code") != 200


@then("提交的数据应该存在")
def verify_fixture_data_exists(fixture_submitted_data):
    """验证fixture数据存在"""
    assert fixture_submitted_data is not None


@then(parsers.parse('数据名称应该是 "{name}"'))
def verify_fixture_data_name(fixture_submitted_data, name):
    """验证fixture数据名称"""
    assert fixture_submitted_data["name"] == name


@then(parsers.parse("数据值应该是 {value:d}"))
def verify_fixture_data_value(fixture_submitted_data, value):
    """验证fixture数据值"""
    assert fixture_submitted_data["value"] == value

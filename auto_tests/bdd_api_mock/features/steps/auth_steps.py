# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 认证模块 BDD 步骤定义
# @Time   : 2026-04-17
# @Author : 毛鹏
"""
认证模块步骤定义
"""

import pytest
from pytest_bdd import given, when, then, parsers
from pytest_bdd.parsers import parse

from auto_tests.bdd_api_mock.data_factory.entities import UserEntityPydantic
from auto_tests.bdd_api_mock.data_factory.builders.auth.auth_builder_pydantic import (
    AuthBuilder,
)
from auto_tests.bdd_api_mock.api_manager import bdd_api_mock


# ==================== Given 步骤 ====================


@given("用户已准备好有效的登录凭据", target_fixture="login_credentials")
def prepare_valid_credentials(table):
    """准备有效的登录凭据"""
    rows = list(table)
    return {"username": rows[0]["username"], "password": rows[0]["password"]}


@given("用户准备了错误的用户名", target_fixture="login_credentials")
def prepare_wrong_username(table):
    """准备错误的用户名"""
    rows = list(table)
    return {"username": rows[0]["username"], "password": rows[0]["password"]}


@given("用户准备了错误的密码", target_fixture="login_credentials")
def prepare_wrong_password(table):
    """准备错误的密码"""
    rows = list(table)
    return {"username": rows[0]["username"], "password": rows[0]["password"]}


@given("用户准备了登录凭据", target_fixture="login_credentials")
def prepare_login_credentials(table):
    """准备登录凭据"""
    rows = list(table)
    return {"username": rows[0]["username"], "password": rows[0]["password"]}


# ==================== When 步骤 ====================


@when("用户使用这些凭据发起登录请求", target_fixture="login_result")
def user_login_with_credentials(login_credentials):
    """用户使用凭据登录"""
    user = UserEntityPydantic.with_credentials(
        username=login_credentials["username"], password=login_credentials["password"]
    )
    builder = AuthBuilder()
    token = builder.login(user)
    return {"token": token, "user": user}


@when("用户使用该令牌获取用户列表", target_fixture="api_response")
def get_users_with_token(logged_in_user):
    """使用令牌获取用户列表"""
    bdd_api_mock.auth.set_token(logged_in_user["token"])
    result = bdd_api_mock.user.get_all_users()
    return result


# ==================== Then 步骤 ====================


@then("登录应该成功")
def login_should_succeed(login_result):
    """验证登录成功"""
    assert login_result["token"] is not None


@then("系统应该返回有效的访问令牌")
def verify_valid_token(login_result):
    """验证返回有效的访问令牌"""
    assert login_result["token"].startswith("mock_token_")


@then("用户ID应该被正确设置")
def verify_user_id_set(login_result):
    """验证用户ID被正确设置"""
    assert login_result["user"].id is not None


@then("登录应该失败")
def login_should_fail(login_result):
    """验证登录失败"""
    assert login_result["token"] is None


@then("系统不应该返回访问令牌")
def verify_no_token(login_result):
    """验证没有返回访问令牌"""
    assert login_result["token"] is None


@then("应该成功获取用户列表")
def verify_users_list_success(api_response):
    """验证成功获取用户列表"""
    assert api_response.get("code") == 200
    assert isinstance(api_response.get("data"), list)

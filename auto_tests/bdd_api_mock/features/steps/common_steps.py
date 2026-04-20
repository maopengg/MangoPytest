# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: BDD 通用步骤定义
# @Time   : 2026-04-17
# @Author : 毛鹏
"""
通用步骤定义 - 被多个feature文件共享的步骤
"""

import pytest
from pytest_bdd import given, when, then, parsers

from auto_tests.bdd_api_mock.data_factory.entities import UserEntityPydantic
from auto_tests.bdd_api_mock.data_factory.builders.auth.auth_builder_pydantic import AuthBuilder
from auto_tests.bdd_api_mock.data_factory.builders.user import UserBuilder
from auto_tests.bdd_api_mock.api_manager import bdd_api_mock


# ==================== Given 步骤 ====================

@given("系统已初始化")
def system_initialized():
    """系统初始化步骤"""
    pass


@given("用户已登录系统", target_fixture="authenticated_user")
def user_logged_in():
    """用户登录步骤"""
    user = UserEntityPydantic.with_credentials(
        username="testuser", password="password123"
    )
    builder = AuthBuilder()
    token = builder.login(user)
    return {"user": user, "token": token}


@given("管理员已登录系统", target_fixture="admin_user_logged_in")
def admin_logged_in():
    """管理员登录步骤"""
    user = UserEntityPydantic.with_credentials(
        username="admin", password="admin123"
    )
    builder = AuthBuilder()
    token = builder.login(user)
    bdd_api_mock.auth.set_token(token)
    return {"user": user, "token": token}


@given("员工已登录系统", target_fixture="employee_logged_in")
def employee_logged_in():
    """员工登录步骤"""
    user = UserEntityPydantic.with_credentials(
        username="employee", password="employee123"
    )
    builder = AuthBuilder()
    token = builder.login(user)
    bdd_api_mock.auth.set_token(token)
    return {"user": user, "token": token}


@given("审批人已登录系统", target_fixture="approver_logged_in")
def approver_logged_in():
    """审批人登录步骤"""
    user = UserEntityPydantic.with_credentials(
        username="dept_manager", password="manager123"
    )
    builder = AuthBuilder()
    token = builder.login(user)
    bdd_api_mock.auth.set_token(token)
    return {"user": user, "token": token}


@given("用户已成功登录", target_fixture="logged_in_user")
def user_already_logged_in():
    """用户已成功登录"""
    user = UserEntityPydantic.with_credentials(
        username="testuser", password="password123"
    )
    builder = AuthBuilder()
    token = builder.login(user)
    bdd_api_mock.auth.set_token(token)
    return {"user": user, "token": token}


# ==================== Then 步骤 ====================

@then(parsers.parse('系统应该返回错误码 {error_code:d}'))
def verify_error_code(error_code, api_response):
    """验证错误码"""
    assert api_response.get("code") == error_code


@then(parsers.parse('错误消息应该包含 "{message}"'))
def verify_error_message(message, api_response):
    """验证错误消息"""
    assert message in api_response.get("message", "")


@then("系统应该返回非成功状态码")
def verify_non_success_status(api_response):
    """验证返回非成功状态码"""
    assert api_response.get("code") != 200


@then(parsers.parse('总共应该创建 {count:d} 个'))
def verify_created_count(count, created_items):
    """验证创建的数量"""
    assert len(created_items) == count

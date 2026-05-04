# -*- coding: utf-8 -*-
"""
登录相关步骤

提供用户登录、权限验证等步骤定义
"""

import hashlib
from typing import Dict, Any

from pytest_bdd import given, when, then, parsers


@given(parsers.parse('用户"{username}"已登录'), target_fixture="logged_in_user")
def user_logged_in_step(username: str, api_client):
    """用户已登录步骤 - 使用共享的 api_client"""
    # 根据用户名确定密码
    if username == "testuser":
        password = "password123"
    elif username == "admin":
        password = "admin"
    else:
        password = "password123"
    password_md5 = hashlib.md5(password.encode()).hexdigest()

    response = api_client.post(
        "/auth/login", {"username": username, "password": password_md5}
    )

    assert response.data.get("code") == 200, f"登录失败: {response.data.get('message')}"

    # token 已在 api_client fixture 中设置
    token = response.data["data"]["token"]

    return {
        "user_id": response.data["data"]["user_id"],
        "username": response.data["data"]["username"],
        "role": response.data["data"]["role"],
        "token": token,
    }


@given(parsers.parse("管理员已登录"), target_fixture="admin_logged_in")
def admin_logged_in_step(api_client):
    """管理员已登录步骤

    注意：由于 testuser 是唯一可用的登录账号，使用 testuser 登录
    但 testuser 不能用于修改和删除操作，这些操作需要通过数据工厂创建测试数据
    """
    return user_logged_in_step("testuser", api_client)


@given(parsers.parse("部门经理已登录"), target_fixture="manager_logged_in")
def manager_logged_in_step(api_client):
    """部门经理已登录步骤"""
    return user_logged_in_step("dept_manager", api_client)


@given(parsers.parse("财务经理已登录"), target_fixture="finance_logged_in")
def finance_logged_in_step(api_client):
    """财务经理已登录步骤"""
    return user_logged_in_step("finance_manager", api_client)


@given(parsers.parse("总经理已登录"), target_fixture="ceo_logged_in")
def ceo_logged_in_step(api_client):
    """总经理已登录步骤"""
    return user_logged_in_step("ceo", api_client)


@when(
    parsers.re(r'用户使用用户名"(?P<username>[^"]+)"和密码"(?P<password>[^"]+)"登录'),
    target_fixture="login_response",
)
def user_login_step(username: str, password: str, api_client):
    """用户登录步骤"""
    # 如果密码不是 MD5 格式，进行 MD5 加密
    if len(password) != 32 or not all(
        c in "0123456789abcdef" for c in password.lower()
    ):
        password = hashlib.md5(password.encode()).hexdigest()

    response = api_client.post(
        "/auth/login", {"username": username, "password": password}
    )

    return response


@then(parsers.parse("登录应该成功"))
def login_should_succeed(login_response):
    """验证登录成功"""
    response_data = (
        login_response.data if hasattr(login_response, "data") else login_response
    )
    assert response_data.get("code") == 200, f"登录失败: {response_data.get('message')}"
    assert response_data.get("data", {}).get("token") is not None


@then(parsers.parse("登录应该失败"))
def login_should_fail(login_response):
    """验证登录失败"""
    response_data = (
        login_response.data if hasattr(login_response, "data") else login_response
    )
    assert response_data.get("code") != 200, "期望登录失败，但实际成功"


@then(parsers.parse("应该返回错误码 {error_code:d}"))
def should_return_error_code(error_code: int, login_response):
    """验证返回错误码"""
    response_data = (
        login_response.data if hasattr(login_response, "data") else login_response
    )
    assert (
        response_data.get("code") == error_code
    ), f"期望错误码 {error_code}，实际 {response_data.get('code')}"

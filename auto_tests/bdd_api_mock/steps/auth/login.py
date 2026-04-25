# -*- coding: utf-8 -*-
"""
登录相关步骤

提供用户登录、权限验证等步骤定义
"""

import hashlib
from typing import Dict, Any

from pytest_bdd import given, when, then, parsers

from auto_tests.bdd_api_mock.api_client import APIClient


@given(parsers.parse('用户"{username}"已登录'), target_fixture="logged_in_user")
def user_logged_in_step(username: str):
    """用户已登录步骤"""
    # 使用默认密码登录
    client = APIClient()

    # 根据用户名确定密码
    if username == "testuser":
        password = "password123"
    elif username == "admin":
        password = "admin"
    else:
        password = "password123"
    password_md5 = hashlib.md5(password.encode()).hexdigest()

    response = client.post(
        "/auth/login", {"username": username, "password": password_md5}
    )

    assert response.get("code") == 200, f"登录失败: {response.get('message')}"

    return {
        "user_id": response["data"]["user_id"],
        "username": response["data"]["username"],
        "role": response["data"]["role"],
        "token": response["data"]["token"],
    }


@given(parsers.parse("管理员已登录"), target_fixture="admin_logged_in")
def admin_logged_in_step():
    """管理员已登录步骤
    
    注意：由于 testuser 是唯一可用的登录账号，使用 testuser 登录
    但 testuser 不能用于修改和删除操作，这些操作需要通过数据工厂创建测试数据
    """
    return user_logged_in_step("testuser")


@given(parsers.parse("部门经理已登录"), target_fixture="manager_logged_in")
def manager_logged_in_step():
    """部门经理已登录步骤"""
    return user_logged_in_step("dept_manager")


@given(parsers.parse("财务经理已登录"), target_fixture="finance_logged_in")
def finance_logged_in_step():
    """财务经理已登录步骤"""
    return user_logged_in_step("finance_manager")


@given(parsers.parse("总经理已登录"), target_fixture="ceo_logged_in")
def ceo_logged_in_step():
    """总经理已登录步骤"""
    return user_logged_in_step("ceo")


@when(
    parsers.re(r'用户使用用户名"(?P<username>[^"]+)"和密码"(?P<password>[^"]+)"登录'),
    target_fixture="login_response",
)
def user_login_step(username: str, password: str):
    """用户登录步骤"""
    client = APIClient()

    # 如果密码不是 MD5 格式，进行 MD5 加密
    if len(password) != 32 or not all(
        c in "0123456789abcdef" for c in password.lower()
    ):
        password = hashlib.md5(password.encode()).hexdigest()

    response = client.post("/auth/login", {"username": username, "password": password})

    return response


@then(parsers.parse("登录应该成功"))
def login_should_succeed(login_response: Dict[str, Any]):
    """验证登录成功"""
    assert (
        login_response.get("code") == 200
    ), f"登录失败: {login_response.get('message')}"
    assert login_response.get("data", {}).get("token") is not None


@then(parsers.parse("登录应该失败"))
def login_should_fail(login_response: Dict[str, Any]):
    """验证登录失败"""
    assert login_response.get("code") != 200, "期望登录失败，但实际成功"


@then(parsers.parse("应该返回错误码 {error_code:d}"))
def should_return_error_code(error_code: int, login_response: Dict[str, Any]):
    """验证返回错误码"""
    assert (
        login_response.get("code") == error_code
    ), f"期望错误码 {error_code}，实际 {login_response.get('code')}"

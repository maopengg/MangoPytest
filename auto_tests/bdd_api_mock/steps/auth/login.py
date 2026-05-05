# -*- coding: utf-8 -*-
"""
登录相关步骤

提供用户登录、权限验证等步骤定义
"""

import hashlib
import os
from typing import Dict, Any

from pytest_bdd import given, when, then, parsers

from core.utils import log


# 缓存已登录用户信息（避免重复登录）
_logged_in_users: Dict[str, Dict[str, Any]] = {}


def _hash_password(password: str) -> str:
    """统一密码加密：如果已经是 MD5 格式则跳过"""
    if len(password) == 32 and all(c in "0123456789abcdef" for c in password.lower()):
        return password
    return hashlib.md5(password.encode()).hexdigest()


def _do_login(api_client, username: str, password: str) -> Dict[str, Any]:
    """统一登录请求，返回完整用户数据"""
    password_md5 = _hash_password(password)

    response = api_client.post(
        "/auth/login", {"username": username, "password": password_md5}
    )

    if response.data.get("code") != 200:
        raise RuntimeError(f"登录失败: {response.data.get('message')}")

    return response.data["data"]


def _set_auth_header(api_client, token: str):
    """设置认证请求头到客户端"""
    api_client.headers["Authorization"] = f"Bearer {token}"
    log.debug("已设置 Authorization 请求头")


@given(parsers.parse('用户"{username}"已登录'), target_fixture="logged_in_user")
def user_logged_in_step(username: str, api_client):
    """用户已登录步骤

    自动将 token 设置到 api_client 默认请求头
    """
    global _logged_in_users

    # 检查全局缓存
    if username in _logged_in_users:
        user_info = _logged_in_users[username]
        _set_auth_header(api_client, user_info["token"])
        log.debug(f"用户 {username} 已从缓存获取")
        return user_info

    # 从环境变量或默认获取密码
    password = os.environ.get(f"TEST_PASSWORD_{username.upper()}", "password123")

    # 执行统一登录
    user_data = _do_login(api_client, username, password)

    # 提取用户信息
    user_info = {
        "user_id": user_data["user_id"],
        "username": user_data["username"],
        "role": user_data["role"],
        "token": user_data["token"],
    }

    # 缓存并设置请求头
    _logged_in_users[username] = user_info
    _set_auth_header(api_client, user_info["token"])
    log.info(f"用户 {username} 登录成功，已缓存并设置请求头")

    return user_info


@given(parsers.parse("管理员已登录"), target_fixture="admin_logged_in")
def admin_logged_in_step(api_client):
    """管理员已登录（默认 testuser）"""
    return user_logged_in_step("testuser", api_client)


@given(parsers.parse("部门经理已登录"), target_fixture="manager_logged_in")
def manager_logged_in_step(api_client):
    """部门经理已登录"""
    return user_logged_in_step("dept_manager", api_client)


@given(parsers.parse("财务经理已登录"), target_fixture="finance_logged_in")
def finance_logged_in_step(api_client):
    """财务经理已登录"""
    return user_logged_in_step("finance_manager", api_client)


@given(parsers.parse("总经理已登录"), target_fixture="ceo_logged_in")
def ceo_logged_in_step(api_client):
    """总经理已登录"""
    return user_logged_in_step("ceo", api_client)


@when(
    parsers.re(r'用户使用用户名"(?P<username>[^"]+)"和密码"(?P<password>[^"]+)"登录'),
    target_fixture="login_response",
)
def user_login_step(username: str, password: str, api_client):
    """用户登录步骤（用于测试登录场景，不自动设置请求头）"""
    password_md5 = _hash_password(password)

    response = api_client.post(
        "/auth/login", {"username": username, "password": password_md5}
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

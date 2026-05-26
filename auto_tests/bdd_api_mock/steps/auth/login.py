# -*- coding: utf-8 -*-
"""
登录相关步骤

提供用户登录、权限验证等步骤定义
"""

import hashlib
import os
import uuid
from typing import Dict, Any

from pytest_bdd import given, when, then, parsers

from core.utils import log
from mangotools.data_processor import DataProcessor


# 缓存已登录用户信息（避免重复登录）
_logged_in_users: Dict[str, Dict[str, Any]] = {}

# 数据处理器
_data_processor = DataProcessor()


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


@given(parsers.parse("未登录用户"), target_fixture="unauthorized_client")
def unauthorized_user_step(api_client):
    """未登录用户（清除认证头）"""
    log.debug("设置为未登录用户")
    # 清除 Authorization 请求头
    if "Authorization" in api_client.headers:
        del api_client.headers["Authorization"]
    return api_client


@given(parsers.parse("使用无效Token"), target_fixture="invalid_token_client")
def invalid_token_step(api_client):
    """使用无效Token"""
    log.debug("设置无效Token")
    api_client.headers["Authorization"] = "Bearer invalid_token_12345"
    return api_client


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


@when(
    parsers.re(
        r'用户使用用户名"(?P<username>[^"]+)"和明文密码"(?P<password>[^"]+)"登录'
    ),
    target_fixture="login_response",
)
def user_login_with_plain_password_step(username: str, password: str, api_client):
    """用户使用明文密码登录步骤（系统应自动进行MD5加密）"""
    log.debug(f"使用明文密码登录: {username}")
    # 直接发送明文密码，让系统自动处理加密
    response = api_client.post(
        "/auth/login", {"username": username, "password": password}
    )
    log.debug(f"明文密码登录响应: {response.data}")
    return response


@when(
    parsers.parse('用户使用空用户名和密码"{password}"登录'),
    target_fixture="login_response",
)
def user_login_with_empty_username_step(password: str, api_client):
    """用户使用空用户名登录"""
    log.debug("使用空用户名登录")
    password_md5 = _hash_password(password)
    response = api_client.post(
        "/auth/login", {"username": "", "password": password_md5}
    )
    log.debug(f"空用户名登录响应: {response.data}")
    return response


@when(
    parsers.parse('用户使用用户名"{username}"和空密码登录'),
    target_fixture="login_response",
)
def user_login_with_empty_password_step(username: str, api_client):
    """用户使用空密码登录"""
    log.debug(f"使用空密码登录: {username}")
    response = api_client.post("/auth/login", {"username": username, "password": ""})
    log.debug(f"空密码登录响应: {response.data}")
    return response


@when(
    parsers.re(r'用户使用用户名"(?P<username>[^"]+)"和密码"(?P<password>[^"]+)"注册'),
    target_fixture="register_response",
)
def user_register_step(username: str, password: str, api_client):
    """用户注册步骤"""
    log.debug(f"用户注册: {username}")
    password_md5 = _hash_password(password)
    email = _data_processor.character_email()
    full_name = _data_processor.character_male_name()
    response = api_client.post(
        "/auth/register",
        {
            "username": username,
            "password": password_md5,
            "role": "user",
            "email": email,
            "full_name": full_name,
        },
    )
    log.debug(f"注册响应: {response.data}")
    return response


@when(
    parsers.parse('用户使用用户名"{username}"和明文密码"{password}"注册'),
    target_fixture="register_response",
)
def user_register_with_plain_password_step(username: str, password: str, api_client):
    """用户使用明文密码注册步骤"""
    log.debug(f"使用明文密码注册: {username}")
    email = _data_processor.character_email()
    full_name = _data_processor.character_male_name()
    response = api_client.post(
        "/auth/register",
        {
            "username": username,
            "password": password,
            "role": "user",
            "email": email,
            "full_name": full_name,
        },
    )
    log.debug(f"明文密码注册响应: {response.data}")
    return response


@when(
    parsers.parse('用户使用MD5密码"{password_md5}"注册'),
    target_fixture="register_response",
)
def user_register_with_md5_password_step(password_md5: str, api_client):
    """用户使用MD5密码注册步骤（不做二次加密）"""
    username = f"AUTO_md5user_{uuid.uuid4().hex[:8]}"
    log.debug(f"使用MD5密码注册: {username}")
    email = _data_processor.character_email()
    full_name = _data_processor.character_male_name()
    response = api_client.post(
        "/auth/register",
        {
            "username": username,
            "password": password_md5,
            "role": "user",
            "email": email,
            "full_name": full_name,
        },
    )
    log.debug(f"MD5密码注册响应: {response.data}")
    return response


@when(
    parsers.parse('用户使用空用户名和密码"{password}"注册'),
    target_fixture="register_response",
)
def user_register_with_empty_username_step(password: str, api_client):
    """用户使用空用户名注册"""
    log.debug("使用空用户名注册")
    password_md5 = _hash_password(password)
    email = _data_processor.character_email()
    full_name = _data_processor.character_male_name()
    response = api_client.post(
        "/auth/register",
        {
            "username": "",
            "password": password_md5,
            "role": "user",
            "email": email,
            "full_name": full_name,
        },
    )
    log.debug(f"空用户名注册响应: {response.data}")
    return response


@when(
    parsers.parse('用户使用随机用户名和密码"{password}"注册'),
    target_fixture="register_response",
)
def user_register_with_random_username_step(password: str, api_client):
    """用户使用随机用户名注册（确保用户名唯一）"""
    username = f"AUTO_testuser_{uuid.uuid4().hex[:8]}"
    log.debug(f"使用随机用户名注册: {username}")
    password_md5 = _hash_password(password)
    email = _data_processor.character_email()
    full_name = _data_processor.character_male_name()
    response = api_client.post(
        "/auth/register",
        {
            "username": username,
            "password": password_md5,
            "role": "user",
            "email": email,
            "full_name": full_name,
        },
    )
    log.debug(f"随机用户名注册响应: {response.data}")
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


@then(parsers.parse("注册应该成功"))
def register_should_succeed(register_response):
    """验证注册成功"""
    response_data = (
        register_response.data
        if hasattr(register_response, "data")
        else register_response
    )
    assert response_data.get("code") == 200, f"注册失败: {response_data.get('message')}"


@then(parsers.parse("注册应该失败"))
def register_should_fail(register_response):
    """验证注册失败"""
    response_data = (
        register_response.data
        if hasattr(register_response, "data")
        else register_response
    )
    assert response_data.get("code") != 200, "期望注册失败，但实际成功"


@then(parsers.parse("注册应该返回错误码 {error_code:d}"))
def register_should_return_error_code(error_code: int, register_response):
    """验证注册返回错误码"""
    response_data = (
        register_response.data
        if hasattr(register_response, "data")
        else register_response
    )
    assert (
        response_data.get("code") == error_code
    ), f"期望错误码 {error_code}，实际 {response_data.get('code')}"

# -*- coding: utf-8 -*-
"""
简单调试测试
"""

from pytest_bdd import scenarios, given, when, then, parsers

# 加载 feature 文件
scenarios("user.feature")


@given('管理员已登录')
def admin_logged_in():
    print("管理员已登录")


@when(parsers.re(r'GET\s+"(?P<path>[^"]+)"'), target_fixture="api_response")
def api_get_step(path: str, mock_api_client):
    """GET 请求步骤"""
    print(f"GET {path}")
    result = mock_api_client.get(path)
    print(f"Result: {result}")
    return result


@then(parsers.parse('响应状态码应该为 {expected_code:d}'))
def check_response(expected_code: int, api_response):
    print(f"api_response: {api_response}")
    actual_code = api_response.get("code", api_response.get("status_code", 0))
    assert actual_code == expected_code, f"期望状态码 {expected_code}，实际 {actual_code}"


@then(parsers.parse('响应数据应该是列表'))
def check_list(api_response):
    assert isinstance(api_response.get("data"), list)


@then(parsers.parse('列表长度应该大于等于 {min_len:d}'))
def check_list_length(min_len: int, api_response):
    assert len(api_response.get("data", [])) >= min_len

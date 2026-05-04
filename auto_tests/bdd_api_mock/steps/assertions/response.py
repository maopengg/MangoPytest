# -*- coding: utf-8 -*-
"""
响应状态码和消息断言

提供验证 HTTP 响应状态码和消息的步骤定义
"""

from typing import Any, Dict

from pytest_bdd import then, parsers


def _get_response_data(api_response):
    """从 api_response 中提取响应数据
    
    支持 APIResponse 对象或 dict 类型的响应数据
    """
    if hasattr(api_response, "data"):
        # APIResponse 对象
        return api_response.data
    elif isinstance(api_response, dict):
        if "response" in api_response:
            # 从 fixture 字典中获取 APIResponse 对象
            response_obj = api_response["response"]
            return response_obj.data if hasattr(response_obj, "data") else response_obj
        return api_response
    return api_response


@then(parsers.parse("response code should be {expected_code:d}"))
def response_code_should_be(expected_code: int, api_response):
    """验证响应状态码"""
    data = _get_response_data(api_response)
    actual_code = data.get("code", data.get("status_code", 0)) if isinstance(data, dict) else 0
    assert (
        actual_code == expected_code
    ), f"期望状态码 {expected_code}，实际 {actual_code}"


@then(parsers.parse("响应状态码应该为 {expected_code:d}"))
def response_code_should_be_cn(
    expected_code: int,
    api_response,
):
    """验证响应状态码（中文）"""
    data = _get_response_data(api_response)
    actual_code = data.get("code", data.get("status_code", 0)) if isinstance(data, dict) else 0
    assert (
        actual_code == expected_code
    ), f"期望状态码 {expected_code}，实际 {actual_code}"


@then(parsers.parse('response message should be "{expected_message}"'))
def response_message_should_be(expected_message: str, api_response):
    """验证响应消息"""
    data = _get_response_data(api_response)
    actual_message = data.get("message", "") if isinstance(data, dict) else ""
    assert (
        actual_message == expected_message
    ), f"期望消息 '{expected_message}'，实际 '{actual_message}'"


@then(parsers.parse('响应消息应该为 "{expected_message}"'))
def response_message_should_be_cn(expected_message: str, api_response):
    """验证响应消息（中文）"""
    data = _get_response_data(api_response)
    actual_message = data.get("message", "") if isinstance(data, dict) else ""
    assert (
        actual_message == expected_message
    ), f"期望消息 '{expected_message}'，实际 '{actual_message}'"


@then(parsers.parse('响应消息应该包含 "{expected_message}"'))
def response_message_should_contain(
    expected_message: str, api_response
):
    """验证响应消息包含"""
    data = _get_response_data(api_response)
    actual_message = data.get("message", "") if isinstance(data, dict) else ""
    assert (
        expected_message in actual_message
    ), f"期望消息包含 '{expected_message}'，实际 '{actual_message}'"

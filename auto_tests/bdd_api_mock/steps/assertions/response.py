# -*- coding: utf-8 -*-
"""
响应状态码和消息断言

提供验证 HTTP 响应状态码和消息的步骤定义
"""

from typing import Any, Dict

from pytest_bdd import then, parsers


@then(parsers.parse("response code should be {expected_code:d}"))
def response_code_should_be(expected_code: int, api_response: Dict[str, Any]):
    """验证响应状态码"""
    actual_code = api_response.get("code", api_response.get("status_code", 0))
    assert (
        actual_code == expected_code
    ), f"期望状态码 {expected_code}，实际 {actual_code}"


@then(parsers.parse("响应状态码应该为 {expected_code:d}"))
def response_code_should_be_cn(
    expected_code: int,
    api_response: Dict[str, Any],
):
    """验证响应状态码（中文）"""
    actual_code = api_response.get("code", api_response.get("status_code", 0))
    assert (
        actual_code == expected_code
    ), f"期望状态码 {expected_code}，实际 {actual_code}"


@then(parsers.parse('response message should be "{expected_message}"'))
def response_message_should_be(expected_message: str, api_response: Dict[str, Any]):
    """验证响应消息"""
    actual_message = api_response.get("message", "")
    assert (
        actual_message == expected_message
    ), f"期望消息 '{expected_message}'，实际 '{actual_message}'"


@then(parsers.parse('响应消息应该为 "{expected_message}"'))
def response_message_should_be_cn(expected_message: str, api_response: Dict[str, Any]):
    """验证响应消息（中文）"""
    actual_message = api_response.get("message", "")
    assert (
        actual_message == expected_message
    ), f"期望消息 '{expected_message}'，实际 '{actual_message}'"


@then(parsers.parse('响应消息应该包含 "{expected_message}"'))
def response_message_should_contain(
    expected_message: str, api_response: Dict[str, Any]
):
    """验证响应消息包含"""
    actual_message = api_response.get("message", "")
    assert (
        expected_message in actual_message
    ), f"期望消息包含 '{expected_message}'，实际 '{actual_message}'"

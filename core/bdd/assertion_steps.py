# -*- coding: utf-8 -*-
"""
通用断言步骤定义

提供跨项目可用的 BDD 断言步骤：
- 响应状态码断言
- 响应数据断言
- 字段存在性检查

使用方法:
    1. 在项目 conftest.py 中导入:
       from core.bdd.assertion_steps import *
"""

from typing import Any, Dict

from pytest_bdd import then, parsers

from core.utils import log


def _get_response_data(api_response: Dict) -> Any:
    """从 api_response 中提取响应数据

    如果响应数据是 dict 且包含 'data' 字段，返回 data 字段的内容
    否则返回整个响应数据
    """
    if not api_response or "response" not in api_response:
        raise ValueError("api_response 为空，请先执行 API 请求步骤")

    response = api_response["response"]

    # 支持 APIResponse 对象或 dict
    if hasattr(response, "data"):
        data = response.data
    else:
        data = response

    # 如果数据是 dict 且包含 'data' 字段，返回内部的 data
    # 这是为了处理 {"code": 200, "data": {...}} 这种格式
    if isinstance(data, dict) and "data" in data:
        return data["data"]

    return data


@then(parsers.parse("响应状态码应该为 {expected_code:d}"))
def response_status_code_should_be(
    expected_code: int,
    api_response: Dict,
):
    """验证响应状态码"""
    response = api_response.get("response")
    if not response:
        raise AssertionError("没有 API 响应")

    actual_code = (
        response.status_code
        if hasattr(response, "status_code")
        else response.get("status_code", 0)
    )

    assert actual_code == expected_code, (
        f"期望状态码 {expected_code}，实际 {actual_code}\n"
        f"响应数据: {getattr(response, 'data', response)}"
    )

    log.info(f"✓ 状态码验证通过: {actual_code}")


@then(parsers.parse('响应数据应该包含字段 "{field}"'))
def response_data_should_contain_field(
    field: str,
    api_response: Dict,
):
    """验证响应数据包含指定字段"""
    data = _get_response_data(api_response)

    # 支持嵌套字段，如 "data.order_no"
    if "." in field:
        parts = field.split(".")
        current = data
        for part in parts:
            assert (
                part in current
            ), f"响应数据中不包含字段 '{field}'（在 '{part}' 处缺失）"
            current = current[part]
    else:
        assert field in data, f"响应数据中不包含字段 '{field}'"

    log.info(f"✓ 字段验证通过: {field}")


@then(parsers.parse('响应数据 "{field}" 应该为 "{expected_value}"'))
def response_data_field_should_be(
    field: str,
    expected_value: str,
    api_response: Dict,
):
    """验证响应数据字段值"""
    data = _get_response_data(api_response)

    # 获取字段值（支持嵌套）
    if "." in field:
        parts = field.split(".")
        current = data
        for part in parts:
            assert part in current, f"响应数据中不包含字段 '{field}'"
            current = current[part]
        actual_value = current
    else:
        assert field in data, f"响应数据中不包含字段 '{field}'"
        actual_value = data[field]

    # 类型转换后比较
    actual_str = str(actual_value)
    assert actual_str == expected_value, (
        f"字段 '{field}' 值不匹配\n" f"期望: {expected_value}\n" f"实际: {actual_str}"
    )

    log.info(f"✓ 字段值验证通过: {field} = {expected_value}")


@then(parsers.parse("响应数据应该是列表"))
def response_data_should_be_list(
    api_response: Dict,
):
    """验证响应数据是列表"""
    data = _get_response_data(api_response)

    # 如果响应有 data 字段，检查 data
    if isinstance(data, dict) and "data" in data:
        actual_data = data["data"]
    else:
        actual_data = data

    assert isinstance(
        actual_data, list
    ), f"响应数据不是列表，实际类型: {type(actual_data).__name__}"

    log.info(f"✓ 数据类型验证通过: 列表 (长度 {len(actual_data)})")


@then(parsers.parse("列表长度应该为 {expected_length:d}"))
def response_list_length_should_be(
    expected_length: int,
    api_response: Dict,
):
    """验证列表长度"""
    data = _get_response_data(api_response)

    # 获取列表数据
    if isinstance(data, dict) and "data" in data:
        actual_data = data["data"]
    else:
        actual_data = data

    assert isinstance(actual_data, list), "响应数据不是列表"

    actual_length = len(actual_data)
    assert actual_length == expected_length, (
        f"列表长度不匹配\n" f"期望: {expected_length}\n" f"实际: {actual_length}"
    )

    log.info(f"✓ 列表长度验证通过: {actual_length}")


@then(parsers.parse('响应消息应该包含 "{expected_message}"'))
def response_message_should_contain(
    expected_message: str,
    api_response: Dict,
):
    """验证响应消息包含指定文本"""
    data = _get_response_data(api_response)

    # 尝试获取消息字段
    message = data.get("message", "") if isinstance(data, dict) else str(data)

    assert expected_message in message, (
        f"响应消息不包含 '{expected_message}'\n" f"实际消息: {message}"
    )

    log.info(f"✓ 消息验证通过: 包含 '{expected_message}'")

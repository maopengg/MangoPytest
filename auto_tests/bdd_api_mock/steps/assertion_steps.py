# -*- coding: utf-8 -*-
"""
断言验证步骤
"""

import json
from typing import Any, Dict

from pytest_bdd import then, parsers


# ==================== 响应状态码断言 ====================


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
    api_response: Dict[str, Any] = None,
    login_response: Dict[str, Any] = None,
):
    """验证响应状态码（中文）"""
    response = api_response or login_response or {}
    actual_code = response.get("code", response.get("status_code", 0))
    assert (
        actual_code == expected_code
    ), f"期望状态码 {expected_code}，实际 {actual_code}"


# ==================== 响应消息断言 ====================


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


# ==================== 响应数据断言 ====================


@then(parsers.parse('response data should contain "{field}"'))
def response_data_should_contain_field(field: str, api_response: Dict[str, Any]):
    """验证响应数据包含字段"""
    data = api_response.get("data", {})
    assert field in data, f"响应数据中不包含字段 '{field}'"


@then(parsers.parse('响应数据应该包含字段 "{field}"'))
def response_data_should_contain_field_cn(field: str, api_response: Dict[str, Any] = None, login_response: Dict[str, Any] = None):
    """验证响应数据包含字段（中文）"""
    response = api_response or login_response or {}
    data = response.get("data", {})
    assert field in data, f"响应数据中不包含字段 '{field}'"


@then(parsers.parse('response data "{field}" should be "{expected_value}"'))
def response_data_field_should_be(
    field: str, expected_value: str, api_response: Dict[str, Any]
):
    """验证响应数据字段值"""
    data = api_response.get("data", {})
    actual_value = data.get(field)
    assert (
        str(actual_value) == expected_value
    ), f"期望 '{field}'='{expected_value}'，实际 '{actual_value}'"


@then(parsers.parse('响应数据 "{field}" 应该为 "{expected_value}"'))
def response_data_field_should_be_cn(
    field: str, expected_value: str, api_response: Dict[str, Any]
):
    """验证响应数据字段值（中文）"""
    data = api_response.get("data", {})
    actual_value = data.get(field)
    assert (
        str(actual_value) == expected_value
    ), f"期望 '{field}'='{expected_value}'，实际 '{actual_value}'"


# ==================== 列表断言 ====================


@then(parsers.parse("response data should be a list"))
def response_data_should_be_list(api_response: Dict[str, Any]):
    """验证响应数据是列表"""
    data = api_response.get("data", [])
    assert isinstance(data, list), f"响应数据不是列表: {type(data)}"


@then(parsers.parse("响应数据应该是列表"))
def response_data_should_be_list_cn(api_response: Dict[str, Any]):
    """验证响应数据是列表（中文）"""
    data = api_response.get("data", [])
    assert isinstance(data, list), f"响应数据不是列表: {type(data)}"


@then(parsers.parse("response data list length should be {expected_length:d}"))
def response_data_list_length_should_be(
    expected_length: int, api_response: Dict[str, Any]
):
    """验证列表长度"""
    data = api_response.get("data", [])
    assert isinstance(data, list), f"响应数据不是列表"
    assert (
        len(data) == expected_length
    ), f"期望列表长度 {expected_length}，实际 {len(data)}"


@then(parsers.parse("列表长度应该为 {expected_length:d}"))
def response_data_list_length_should_be_cn(
    expected_length: int, api_response: Dict[str, Any]
):
    """验证列表长度（中文）"""
    data = api_response.get("data", [])
    assert isinstance(data, list), f"响应数据不是列表"
    assert (
        len(data) == expected_length
    ), f"期望列表长度 {expected_length}，实际 {len(data)}"


@then(parsers.parse("列表长度应该大于等于 {expected_length:d}"))
def response_data_list_length_should_be_gte_cn(
    expected_length: int, api_response: Dict[str, Any]
):
    """验证列表长度大于等于（中文）"""
    data = api_response.get("data", [])
    assert isinstance(data, list), f"响应数据不是列表"
    assert (
        len(data) >= expected_length
    ), f"期望列表长度 >= {expected_length}，实际 {len(data)}"


# ==================== 数据库断言 ====================


@then(parsers.parse('数据库中存在"{entity_name}":'))
def db_should_contain_entity(entity_name: str, docstring, db_session):
    """验证数据库中存在实体"""
    from auto_tests.bdd_api_mock.factories.specs import ENTITY_FACTORY_MAP
    from auto_tests.bdd_api_mock.repos import (
        UserRepo,
        ProductRepo,
        OrderRepo,
        DataSubmissionRepo,
        FileRepo,
        ReimbursementRepo,
    )

    expected_data = json.loads(docstring) if docstring else {}

    # 根据实体名称获取 Repository
    repo_map = {
        "用户": UserRepo,
        "产品": ProductRepo,
        "订单": OrderRepo,
        "数据": DataSubmissionRepo,
        "文件": FileRepo,
        "报销": ReimbursementRepo,
    }

    repo_class = repo_map.get(entity_name)
    if not repo_class:
        raise ValueError(f"未知的实体类型: {entity_name}")

    repo = repo_class(db_session)

    # 简单验证：检查是否有数据
    count = repo.count()
    assert count > 0, f"数据库中不存在 {entity_name}"


@then(parsers.parse('数据库中"{entity_name}"数量应该为 {expected_count:d}'))
def db_entity_count_should_be(entity_name: str, expected_count: int, db_session):
    """验证数据库中实体数量"""
    from auto_tests.bdd_api_mock.repos import (
        UserRepo,
        ProductRepo,
        OrderRepo,
        DataSubmissionRepo,
        FileRepo,
        ReimbursementRepo,
    )

    repo_map = {
        "用户": UserRepo,
        "产品": ProductRepo,
        "订单": OrderRepo,
        "数据": DataSubmissionRepo,
        "文件": FileRepo,
        "报销": ReimbursementRepo,
    }

    repo_class = repo_map.get(entity_name)
    if not repo_class:
        raise ValueError(f"未知的实体类型: {entity_name}")

    repo = repo_class(db_session)
    actual_count = repo.count()
    assert (
        actual_count == expected_count
    ), f"期望 {entity_name} 数量 {expected_count}，实际 {actual_count}"

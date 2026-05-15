# -*- coding: utf-8 -*-
"""
响应数据和数据库断言

提供验证响应数据字段、列表和数据库状态的步骤定义
"""

from typing import Any, Dict

from pytest_bdd import then, parsers


@then(parsers.parse('response data should contain "{field}"'))
def response_data_should_contain_field(field: str, api_response: Dict[str, Any]):
    """验证响应数据包含字段"""
    data = api_response.get("data", {})
    assert field in data, f"响应数据中不包含字段 '{field}'"


@then(parsers.parse('响应数据应该包含字段 "{field}"'))
def response_data_should_contain_field_cn(
    field: str,
    api_response: Dict[str, Any],
):
    """验证响应数据包含字段（中文）"""
    data = api_response.get("data", {})
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


@then(parsers.parse('数据库中存在"{entity_name}"'))
def db_should_contain_entity_simple(entity_name: str, db_session):
    """验证数据库中存在实体（简单版本，不带docstring）"""
    from auto_tests.bdd_api_mock.repos import (
        UserRepo,
        ProductRepo,
        OrderRepo,
        DataSubmissionRepo,
        FileRepo,
        ReimbursementRepo,
    )

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

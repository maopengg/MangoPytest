# -*- coding: utf-8 -*-
"""
通用断言步骤定义

提供跨项目可用的 BDD 断言步骤：
- 响应状态码断言
- 响应字段断言（检查 code/message 等元数据）
- 响应数据断言（检查 data 内的业务数据）
- 字段存在性检查

使用方法:
    1. 在项目 conftest.py 中导入:
       from core.bdd.assertion_steps import *

响应格式约定:
    标准 API 响应格式：
    {
        "code": 200,
        "message": "成功",
        "data": {业务数据} 或 null
    }
"""

from typing import Any, Dict

from pytest_bdd import then, parsers

from core.models.api import APIResponse
from core.utils import log


@then(parsers.parse("响应状态码应该为 {expected_code:d}"))
def response_status_code_should_be(expected_code: int, api_response: Dict):
    """验证 HTTP 响应状态码"""
    response: APIResponse = api_response["response"]
    actual_code = response.status_code

    assert actual_code == expected_code, (
        f"期望状态码 {expected_code}，实际 {actual_code}"
    )

    log.info(f"✓ 状态码验证通过: {actual_code}")


@then(parsers.parse('响应字段 "{field}" 应该为 "{expected_value}"'))
def response_field_should_be(field: str, expected_value: str, api_response: Dict):
    """验证响应 JSON 中的字段值（用于检查 code/message 等元数据）

    示例:
        那么 响应字段 "code" 应该为 "200"
        那么 响应字段 "message" 应该为 "操作成功"
    """
    response: APIResponse = api_response["response"]
    data = response.data

    assert isinstance(data, dict), f"响应数据不是字典，实际类型: {type(data).__name__}"
    assert field in data, f"响应中不包含字段 '{field}'"

    actual_value = data[field]
    actual_str = str(actual_value)
    assert actual_str == expected_value, (
        f"字段 '{field}' 值不匹配\n期望: {expected_value}\n实际: {actual_str}"
    )

    log.info(f"✓ 响应字段验证通过: {field} = {expected_value}")


@then(parsers.parse('响应数据 "{field}" 应该为 "{expected_value}"'))
def response_data_field_should_be(field: str, expected_value: str, api_response: Dict):
    """验证业务数据中的字段值（检查 data 字段内的数据）

    示例:
        那么 响应数据 "name" 应该为 "张三"
        那么 响应数据 "status" 应该为 "active"
    """
    response: APIResponse = api_response["response"]
    response_json = response.data

    # 获取业务数据（响应 JSON 中的 data 字段）
    if isinstance(response_json, dict) and "data" in response_json:
        business_data = response_json["data"]
    else:
        business_data = response_json

    assert business_data is not None, "响应中 data 字段为 null"
    assert isinstance(business_data, dict), f"业务数据不是字典，实际类型: {type(business_data).__name__}"
    assert field in business_data, f"业务数据中不包含字段 '{field}'"

    actual_value = business_data[field]
    actual_str = str(actual_value)
    assert actual_str == expected_value, (
        f"字段 '{field}' 值不匹配\n期望: {expected_value}\n实际: {actual_str}"
    )

    log.info(f"✓ 响应数据验证通过: {field} = {expected_value}")


@then(parsers.parse('响应数据应该包含字段 "{field}"'))
def response_data_should_contain_field(field: str, api_response: Dict):
    """验证业务数据中包含指定字段"""
    response: APIResponse = api_response["response"]
    response_json = response.data

    # 获取业务数据（响应 JSON 中的 data 字段）
    if isinstance(response_json, dict) and "data" in response_json:
        business_data = response_json["data"]
    else:
        business_data = response_json

    assert business_data is not None, "响应中 data 字段为 null"

    # 支持嵌套字段，如 "user.name"
    if "." in field:
        parts = field.split(".")
        current = business_data
        for part in parts:
            assert part in current, f"业务数据中不包含字段 '{field}'（在 '{part}' 处缺失）"
            current = current[part]
    else:
        assert field in business_data, f"业务数据中不包含字段 '{field}'"

    log.info(f"✓ 字段验证通过: {field}")


@then(parsers.parse("响应数据应该是列表"))
def response_data_should_be_list(api_response: Dict):
    """验证业务数据是列表"""
    response: APIResponse = api_response["response"]
    response_json = response.data

    # 获取业务数据（响应 JSON 中的 data 字段）
    if isinstance(response_json, dict) and "data" in response_json:
        business_data = response_json["data"]
    else:
        business_data = response_json

    assert isinstance(business_data, list), (
        f"业务数据不是列表，实际类型: {type(business_data).__name__}"
    )

    log.info(f"✓ 数据类型验证通过: 列表 (长度 {len(business_data)})")


@then(parsers.parse("列表长度应该为 {expected_length:d}"))
def response_list_length_should_be(expected_length: int, api_response: Dict):
    """验证列表长度"""
    response: APIResponse = api_response["response"]
    response_json = response.data

    # 获取业务数据（响应 JSON 中的 data 字段）
    if isinstance(response_json, dict) and "data" in response_json:
        business_data = response_json["data"]
    else:
        business_data = response_json

    assert isinstance(business_data, list), "业务数据不是列表"

    actual_length = len(business_data)
    assert actual_length == expected_length, (
        f"列表长度不匹配\n期望: {expected_length}\n实际: {actual_length}"
    )

    log.info(f"✓ 列表长度验证通过: {actual_length}")


@then(parsers.parse("列表长度应该大于等于 {expected_length:d}"))
def response_list_length_should_be_gte(expected_length: int, api_response: Dict):
    """验证列表长度大于等于指定值"""
    response: APIResponse = api_response["response"]
    response_json = response.data

    # 获取业务数据（响应 JSON 中的 data 字段）
    if isinstance(response_json, dict) and "data" in response_json:
        business_data = response_json["data"]
    else:
        business_data = response_json

    assert isinstance(business_data, list), "业务数据不是列表"

    actual_length = len(business_data)
    assert actual_length >= expected_length, (
        f"列表长度不满足条件\n期望: >= {expected_length}\n实际: {actual_length}"
    )

    log.info(f"✓ 列表长度验证通过: {actual_length} >= {expected_length}")


@then(parsers.parse('响应消息应该包含 "{expected_message}"'))
def response_message_should_contain(expected_message: str, api_response: Dict):
    """验证响应消息包含指定文本"""
    response: APIResponse = api_response["response"]
    data = response.data

    message = data.get("message", "") if isinstance(data, dict) else str(data)

    assert expected_message in message, (
        f"响应消息不包含 '{expected_message}'\n实际消息: {message}"
    )

    log.info(f"✓ 消息验证通过: 包含 '{expected_message}'")


@then(parsers.parse('数据库中存在"{entity_name}"'))
def entity_exists_in_database(entity_name: str, entity_context, entity_factory_map: dict):
    """验证数据库中存在指定实体

    检查上下文中是否存在该实体的别名
    """
    alias = entity_name

    try:
        entity = entity_context.get(alias)
        assert entity is not None, f"数据库中不存在 '{entity_name}'"
        log.info(f"✓ 数据库验证通过: '{entity_name}' 存在 (id={getattr(entity, 'id', 'N/A')})")
    except KeyError:
        raise AssertionError(f"数据库中不存在 '{entity_name}'，请先创建实体")

# -*- coding: utf-8 -*-
"""
API BDD 集成步骤 - API 响应断言

提供针对 API 响应的通用断言步骤，依赖 api_response fixture。
这些步骤是对 core.dal.bdd_steps 的封装，专门针对 API 响应数据。
"""

from typing import Any
from pytest_bdd import then, parsers
from core.dal import expect
from core.utils import log


# ==================== Then 步骤 - 状态码断言 ====================

@then(parsers.cfparse('响应状态码为 {status_code:d}'))
def verify_response_status_code(api_response, status_code: int):
    """
    验证响应状态码

    示例:
      那么 响应状态码为 200
    """
    # 支持 dict 类型（包含 status_code 键）或对象类型
    if isinstance(api_response, dict):
        actual_status = api_response.get('status_code')
    else:
        actual_status = api_response.status_code
    log.debug(f"验证状态码: 期望={status_code}, 实际={actual_status}")
    assert actual_status == status_code, \
        f"期望状态码 {status_code}，实际 {actual_status}"


@then(parsers.cfparse('响应状态码应该在 {min_code:d} 和 {max_code:d} 之间'))
def verify_response_status_code_in_range(api_response, min_code: int, max_code: int):
    """
    验证响应状态码在指定范围内

    示例:
      那么 响应状态码应该在 200 和 299 之间
    """
    actual_status = api_response.status_code
    log.debug(f"验证状态码范围: {min_code} <= {actual_status} <= {max_code}")
    assert min_code <= actual_status <= max_code, \
        f"状态码 {actual_status} 不在范围 [{min_code}, {max_code}] 内"


# ==================== Then 步骤 - 响应头断言 ====================

@then(parsers.cfparse('响应头 {header} 为 {expected}'))
def verify_response_header_equals(api_response, header: str, expected: str):
    """
    验证响应头等于期望值

    示例:
      那么 响应头 Content-Type 为 application/json
    """
    actual_value = api_response.headers.get(header, "")
    log.debug(f"验证响应头 {header}: 期望={expected}, 实际={actual_value}")
    assert actual_value == expected, \
        f"响应头 {header} 期望 '{expected}'，实际 '{actual_value}'"


@then(parsers.cfparse('响应头 {header} 包含 {expected}'))
def verify_response_header_contains(api_response, header: str, expected: str):
    """
    验证响应头包含指定值

    示例:
      那么 响应头 Content-Type 包含 application/json
    """
    actual_value = api_response.headers.get(header, "")
    log.debug(f"验证响应头 {header} 包含: {expected}")
    assert expected in actual_value, \
        f"响应头 {header} '{actual_value}' 不包含 '{expected}'"


# ==================== Then 步骤 - 响应体断言（封装 DAL） ====================

@then(parsers.cfparse('响应数据匹配:\n{expression}'))
def verify_response_matches(api_response, expression: str):
    """
    使用 DAL 表达式验证响应数据

    示例:
      那么 响应数据匹配:
        success = true
        data.content.size > 0
    """
    log.debug(f"DAL 验证: {expression.strip()}")
    expect(api_response.data).should(expression.strip())


@then(parsers.cfparse('响应数据匹配表格:\n{table}'))
def verify_response_matches_table(api_response, table: str):
    """
    使用 DAL 表格验证响应数据

    示例:
      那么 响应数据匹配表格:
        | id | name  |
        | 1  | Alice |
        | 2  | Bob   |
    """
    log.debug(f"DAL 表格验证")
    expect(api_response.data).should(table.strip())


@then(parsers.cfparse('响应数据符合:\n{structure}'))
def verify_response_structure(api_response, structure: str):
    """
    验证响应数据符合指定结构（宽容匹配）

    示例:
      那么 响应数据符合:
        : {
          success: true
          data: **
        }
    """
    log.debug(f"结构验证")
    expect(api_response.data).should(structure.strip())


@then(parsers.cfparse('响应数据严格符合:\n{structure}'))
def verify_response_structure_strict(api_response, structure: str):
    """
    验证响应数据严格符合指定结构（不允许多余字段）

    示例:
      那么 响应数据严格符合:
        = {
          success: true
          data: **
        }
    """
    log.debug(f"严格结构验证")
    expect(api_response.data).should(structure.strip())


# ==================== Then 步骤 - 响应字段断言（简化版） ====================

@then(parsers.cfparse('{path} 为 {expected}'))
def verify_response_path_equals(api_response, path: str, expected: str):
    """
    验证响应体路径等于期望值

    示例:
      那么 success 为 true
      那么 data.status 为 ACTIVE
    """
    expression = f"{path} = {expected}"
    log.debug(f"验证: {expression}")
    # 支持 dict 类型或对象类型
    if isinstance(api_response, dict):
        data = api_response.get('data')
    else:
        data = api_response.data
    expect(data).should(expression)


@then(parsers.cfparse('{path} 为 {expected:d}'))
def verify_response_path_equals_int(api_response, path: str, expected: int):
    """
    验证响应体路径等于整数值

    示例:
      那么 code 为 200
      那么 data.total 为 100
    """
    expression = f"{path} = {expected}"
    log.debug(f"验证: {expression}")
    # 支持 dict 类型或对象类型
    if isinstance(api_response, dict):
        data = api_response.get('data')
    else:
        data = api_response.data
    expect(data).should(expression)


@then(parsers.cfparse('{path} 不为 {expected:d}'))
def verify_response_path_not_equals_int(api_response, path: str, expected: int):
    """
    验证响应体路径不等于整数值

    示例:
      那么 code 不为 200
      那么 data.status 不为 404
    """
    expression = f"{path} != {expected}"
    log.debug(f"验证: {expression}")
    if isinstance(api_response, dict):
        data = api_response.get('data')
    else:
        data = api_response.data
    expect(data).should(expression)


@then(parsers.cfparse('{path} 大于 {value:d}'))
def verify_response_path_greater_than(api_response, path: str, value: int):
    """
    验证响应体路径大于指定值

    示例:
      那么 data.total 大于 100
    """
    expression = f"{path} > {value}"
    log.debug(f"验证: {expression}")
    expect(api_response.data).should(expression)


@then(parsers.cfparse('{path} 小于 {value:d}'))
def verify_response_path_less_than(api_response, path: str, value: int):
    """
    验证响应体路径小于指定值

    示例:
      那么 data.age 小于 100
    """
    expression = f"{path} < {value}"
    log.debug(f"验证: {expression}")
    expect(api_response.data).should(expression)


@then(parsers.cfparse('{path} 包含 {expected}'))
def verify_response_path_contains(api_response, path: str, expected: str):
    """
    验证响应体路径包含指定值

    示例:
      那么 data.name 包含 张三
    """
    expression = f"{path} contains '{expected}'"
    log.debug(f"验证: {expression}")
    expect(api_response.data).should(expression)


@then(parsers.cfparse('{path} 以 {prefix} 开头'))
def verify_response_path_starts_with(api_response, path: str, prefix: str):
    """
    验证响应体路径以指定前缀开头

    示例:
      那么 data.orderNo 以 ORD- 开头
    """
    expression = f"{path} starts with '{prefix}'"
    log.debug(f"验证: {expression}")
    expect(api_response.data).should(expression)


@then(parsers.cfparse('{path} 以 {suffix} 结尾'))
def verify_response_path_ends_with(api_response, path: str, suffix: str):
    """
    验证响应体路径以指定后缀结尾

    示例:
      那么 data.email 以 @example.com 结尾
    """
    expression = f"{path} ends with '{suffix}'"
    log.debug(f"验证: {expression}")
    expect(api_response.data).should(expression)


@then(parsers.cfparse('{path} 匹配 {pattern}'))
def verify_response_path_matches_pattern(api_response, path: str, pattern: str):
    """
    验证响应体路径匹配正则表达式

    示例:
      那么 data.orderId 匹配 /ORD-\d+/
    """
    expression = f"{path} = {pattern}"
    log.debug(f"验证: {expression}")
    expect(api_response.data).should(expression)


@then(parsers.parse('data 包含 {expected}'))
def verify_data_contains_value(api_response, expected: str):
    """
    验证响应 data 数组中任意元素的任意字段包含指定值

    示例:
      那么 data 包含 中国大陆
    """
    # 支持 dict 类型或对象类型
    if isinstance(api_response, dict):
        data = api_response.get('data')
    else:
        data = api_response.data

    log.debug(f"验证 data 数组是否包含值: {expected}")

    if not isinstance(data, list):
        assert False, f"data 不是数组，实际类型: {type(data)}"

    # 在数组中查找包含指定值的元素
    found = False
    for item in data:
        if isinstance(item, dict):
            # 检查任意字段的值是否匹配
            for key, value in item.items():
                if value == expected or str(value) == expected:
                    found = True
                    break
        if found:
            break

    assert found, f"data 数组中未找到包含 '{expected}' 的元素"


# ==================== Then 步骤 - 存在性和类型断言 ====================

@then(parsers.cfparse('{path} 存在'))
def verify_response_path_exists(api_response, path: str):
    """
    验证响应体路径存在（不为 null）

    示例:
      那么 data.id 存在
    """
    expression = f"{path} is NotNull"
    log.debug(f"验证: {expression}")
    expect(api_response.data).should(expression)


@then(parsers.cfparse('{path} 为 true'))
def verify_response_path_is_true(api_response, path: str):
    """
    验证响应体路径为 true

    示例:
      那么 success 为 true
    """
    expression = f"{path} = true"
    log.debug(f"验证: {expression}")
    expect(api_response.data).should(expression)


@then(parsers.cfparse('{path} 为 false'))
def verify_response_path_is_false(api_response, path: str):
    """
    验证响应体路径为 false

    示例:
      那么 hasError 为 false
    """
    expression = f"{path} = false"
    log.debug(f"验证: {expression}")
    expect(api_response.data).should(expression)


@then(parsers.cfparse('{path} 符合 schema {schema}'))
def verify_response_path_with_schema(api_response, path: str, schema: str):
    """
    验证响应体路径符合指定 schema

    示例:
      那么 data.email 符合 schema ValidEmail
    """
    expression = f"{path} is {schema}"
    log.debug(f"验证: {expression}")
    expect(api_response.data).should(expression)


# ==================== Then 步骤 - 列表/集合断言 ====================

@then(parsers.cfparse('{path} 大小为 {size:d}'))
def verify_response_path_size_equals(api_response, path: str, size: int):
    """
    验证响应体路径大小等于指定值

    示例:
      那么 data.items 大小为 10
    """
    expression = f"{path}.size = {size}"
    log.debug(f"验证: {expression}")
    expect(api_response.data).should(expression)


@then(parsers.cfparse('{path} 大小大于 {size:d}'))
def verify_response_path_size_greater_than(api_response, path: str, size: int):
    """
    验证响应体路径大小大于指定值

    示例:
      那么 data.items 大小大于 0
    """
    expression = f"{path}.size > {size}"
    log.debug(f"验证: {expression}")
    # 支持 dict 类型或对象类型
    if isinstance(api_response, dict):
        data = api_response.get('data')
    else:
        data = api_response.data
    expect(data).should(expression)


@then(parsers.cfparse('{path} 不为空'))
def verify_response_path_not_empty(api_response, path: str):
    """
    验证响应体路径不为空

    示例:
      那么 data.items 不为空
    """
    expression = f"{path}.size > 0"
    log.debug(f"验证: {expression}")
    # 支持 dict 类型或对象类型
    if isinstance(api_response, dict):
        data = api_response.get('data')
    else:
        data = api_response.data
    expect(data).should(expression)


# ==================== Then 步骤 - 范围断言 ====================

@then(parsers.cfparse('{path} 在 {min_val:d} 和 {max_val:d} 之间'))
def verify_response_path_in_range(api_response, path: str, min_val: int, max_val: int):
    """
    验证响应体路径在指定范围内

    示例:
      那么 data.age 在 18 和 60 之间
    """
    expression = f"{path} >= {min_val} and {path} <= {max_val}"
    log.debug(f"验证: {expression}")
    expect(api_response.data).should(expression)


# ==================== Then 步骤 - 异步断言 ====================

@then(parsers.cfparse('最终 {path} 为 {expected}'))
def verify_response_path_eventually_equals(api_response, path: str, expected: str):
    """
    异步验证：最终响应路径应该等于期望值（轮询等待）

    示例:
      那么 最终 data.status 为 completed
    """
    expression = f"::eventually {path} = {expected}"
    log.debug(f"异步验证: {expression}")
    expect(api_response.data).should(expression)

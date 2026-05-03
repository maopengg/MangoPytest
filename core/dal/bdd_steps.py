# -*- coding: utf-8 -*-
"""
DAL BDD 集成步骤 - 通用数据断言

提供基于 DAL 的通用数据断言步骤，与具体的 API 响应无关。
所有步骤都使用 `data` 参数，可以验证任何数据对象。
"""

from typing import Any
from pytest_bdd import then, parsers, given
from core.dal import expect
from core.utils import log


# ==================== Given 步骤 ====================

@given(parsers.cfparse('数据为:\n{data}'), target_fixture='data')
def given_data(data: str):
    """
    提供测试数据

    示例:
      假如 数据为:
        {name: "张三", age: 25}
    """
    import json
    return json.loads(data.strip())


@given(parsers.cfparse('列表数据为:\n{data}'), target_fixture='data')
def given_list_data(data: str):
    """
    提供列表测试数据

    示例:
      假如 列表数据为:
        [{id: 1}, {id: 2}]
    """
    import json
    return json.loads(data.strip())


# ==================== Then 步骤 - 通用 DAL 断言 ====================

@then(parsers.cfparse('数据应该匹配:\n{expression}'))
def verify_data_matches(data: Any, expression: str):
    """
    使用 DAL 表达式验证数据

    这是最通用的断言，可以使用任何 DAL 表达式

    示例:
      那么 数据应该匹配:
        success = true
        data.content.size > 0
        data.name contains '张三'
    """
    log.debug(f"DAL 验证: {expression.strip()}")
    expect(data).should(expression.strip())


@then(parsers.cfparse('数据应该匹配表格:\n{table}'))
def verify_data_matches_table(data: Any, table: str):
    """
    使用 DAL 表格验证数据

    示例:
      那么 数据应该匹配表格:
        | id | name  |
        | 1  | Alice |
        | 2  | Bob   |
    """
    log.debug(f"DAL 表格验证")
    expect(data).should(table.strip())


# ==================== Then 步骤 - 简化版常用断言 ====================

@then(parsers.cfparse('{path} 应该等于 {expected}'))
def verify_path_equals(data: Any, path: str, expected: str):
    """
    验证路径等于期望值

    示例:
      那么 success 应该等于 true
      那么 data.status 应该等于 ACTIVE
      那么 data.user.name 应该等于 张三
    """
    expression = f"{path} = {expected}"
    log.debug(f"验证: {expression}")
    expect(data).should(expression)


@then(parsers.cfparse('{path} 应该大于 {value:d}'))
def verify_path_greater_than(data: Any, path: str, value: int):
    """
    验证路径大于指定值

    示例:
      那么 data.total 应该大于 100
      那么 items.size 应该大于 0
    """
    expression = f"{path} > {value}"
    log.debug(f"验证: {expression}")
    expect(data).should(expression)


@then(parsers.cfparse('{path} 应该小于 {value:d}'))
def verify_path_less_than(data: Any, path: str, value: int):
    """
    验证路径小于指定值

    示例:
      那么 data.age 应该小于 100
    """
    expression = f"{path} < {value}"
    log.debug(f"验证: {expression}")
    expect(data).should(expression)


@then(parsers.cfparse('{path} 应该包含 {expected}'))
def verify_path_contains(data: Any, path: str, expected: str):
    """
    验证路径包含指定值

    示例:
      那么 data.name 应该包含 张三
      那么 data.email 应该包含 @example.com
    """
    expression = f"{path} contains '{expected}'"
    log.debug(f"验证: {expression}")
    expect(data).should(expression)


@then(parsers.cfparse('{path} 应该以 {prefix} 开头'))
def verify_path_starts_with(data: Any, path: str, prefix: str):
    """
    验证路径以指定前缀开头

    示例:
      那么 data.orderNo 应该以 ORD- 开头
    """
    expression = f"{path} starts with '{prefix}'"
    log.debug(f"验证: {expression}")
    expect(data).should(expression)


@then(parsers.cfparse('{path} 应该以 {suffix} 结尾'))
def verify_path_ends_with(data: Any, path: str, suffix: str):
    """
    验证路径以指定后缀结尾

    示例:
      那么 data.email 应该以 @example.com 结尾
    """
    expression = f"{path} ends with '{suffix}'"
    log.debug(f"验证: {expression}")
    expect(data).should(expression)


@then(parsers.cfparse('{path} 应该匹配 {pattern}'))
def verify_path_matches_pattern(data: Any, path: str, pattern: str):
    """
    验证路径匹配正则表达式

    示例:
      那么 data.orderId 应该匹配 /ORD-\d+/
    """
    expression = f"{path} = {pattern}"
    log.debug(f"验证: {expression}")
    expect(data).should(expression)


# ==================== Then 步骤 - 存在性和类型断言 ====================

@then(parsers.cfparse('{path} 应该存在'))
def verify_path_exists(data: Any, path: str):
    """
    验证路径存在（不为 null）

    示例:
      那么 data.id 应该存在
    """
    expression = f"{path} is NotNull"
    log.debug(f"验证: {expression}")
    expect(data).should(expression)


@then(parsers.cfparse('{path} 应该为 true'))
def verify_path_is_true(data: Any, path: str):
    """
    验证路径为 true

    示例:
      那么 success 应该为 true
    """
    expression = f"{path} = true"
    log.debug(f"验证: {expression}")
    expect(data).should(expression)


@then(parsers.cfparse('{path} 应该为 false'))
def verify_path_is_false(data: Any, path: str):
    """
    验证路径为 false

    示例:
      那么 hasError 应该为 false
    """
    expression = f"{path} = false"
    log.debug(f"验证: {expression}")
    expect(data).should(expression)


@then(parsers.cfparse('{path} 应该符合 schema {schema}'))
def verify_path_with_schema(data: Any, path: str, schema: str):
    """
    验证路径符合指定 schema

    示例:
      那么 data.email 应该符合 schema ValidEmail
      那么 data.createdAt 应该符合 schema Instant
    """
    expression = f"{path} is {schema}"
    log.debug(f"验证: {expression}")
    expect(data).should(expression)


# ==================== Then 步骤 - 列表/集合断言 ====================

@then(parsers.cfparse('{path} 大小应该为 {size:d}'))
def verify_path_size_equals(data: Any, path: str, size: int):
    """
    验证路径大小等于指定值

    示例:
      那么 data.items 大小应该为 10
      那么 data.list.size 应该为 5
    """
    expression = f"{path}.size = {size}"
    log.debug(f"验证: {expression}")
    expect(data).should(expression)


@then(parsers.cfparse('{path} 大小应该大于 {size:d}'))
def verify_path_size_greater_than(data: Any, path: str, size: int):
    """
    验证路径大小大于指定值

    示例:
      那么 data.items 大小应该大于 0
    """
    expression = f"{path}.size > {size}"
    log.debug(f"验证: {expression}")
    expect(data).should(expression)


@then(parsers.cfparse('{path} 不应该为空'))
def verify_path_not_empty(data: Any, path: str):
    """
    验证路径不为空

    示例:
      那么 data.items 不应该为空
    """
    expression = f"{path}.size > 0"
    log.debug(f"验证: {expression}")
    expect(data).should(expression)


# ==================== Then 步骤 - 范围断言 ====================

@then(parsers.cfparse('{path} 应该在 {min_val:d} 和 {max_val:d} 之间'))
def verify_path_in_range(data: Any, path: str, min_val: int, max_val: int):
    """
    验证路径在指定范围内

    示例:
      那么 data.age 应该在 18 和 60 之间
    """
    expression = f"{path} >= {min_val} and {path} <= {max_val}"
    log.debug(f"验证: {expression}")
    expect(data).should(expression)


# ==================== Then 步骤 - 结构断言 ====================

@then(parsers.cfparse('数据应该符合:\n{structure}'))
def verify_data_structure(data: Any, structure: str):
    """
    验证数据符合指定结构（宽容匹配）

    示例:
      那么 数据应该符合:
        : {
          success: true
          data: **
        }
    """
    log.debug(f"结构验证")
    expect(data).should(structure.strip())


@then(parsers.cfparse('数据应该严格符合:\n{structure}'))
def verify_data_structure_strict(data: Any, structure: str):
    """
    验证数据严格符合指定结构（不允许多余字段）

    示例:
      那么 数据应该严格符合:
        = {
          success: true
          data: **
        }
    """
    log.debug(f"严格结构验证")
    expect(data).should(structure.strip())

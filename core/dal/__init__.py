"""
DAL (Data Assertion Language) - 数据断言语言

提供类似 Java TestCharm DAL 的表达式语言，用于测试数据验证。

基本用法:
    from mangotools.dal import expect

    # 基础断言
    expect(1).should("= 1")
    expect("hello").should("= 'hello'")

    # 对象断言
    expect({"name": "张三", "age": 25}).should(": { name: '张三', age: 25 }")

    # 列表断言
    expect([1, 2, 3]).should(".size = 3")

    # 表格断言
    expect([{"id": 1}, {"id": 2}]).should("| id |\n| 1  |\n| 2  |")

    # Schema 验证
    expect({"email": "test@example.com"}).should(": { email is ValidEmail }")
"""

from .assertions import expect, Expectation
from .accessors import get, Accessor
from .schema import (
    SchemaRegistry,
    SchemaValidationResult,
    register_schema,
    validate_schema,
    list_schemas,
)
from .core.operators import Operators, CompareResult

# BDD 步骤（导入时会自动注册 pytest-bdd 步骤）
from . import bdd_steps

__all__ = [
    'expect',
    'Expectation',
    'get',
    'Accessor',
    'SchemaRegistry',
    'SchemaValidationResult',
    'register_schema',
    'validate_schema',
    'list_schemas',
    'Operators',
    'CompareResult',
    'bdd_steps',
]

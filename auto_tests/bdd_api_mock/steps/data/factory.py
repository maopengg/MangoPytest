# -*- coding: utf-8 -*-
"""
数据准备步骤 - 使用 factory_boy

提供使用 factory_boy 创建测试数据的步骤定义
"""

import json
from typing import Any, Dict

from pytest_bdd import given, parsers

from auto_tests.bdd_api_mock.factories.specs import ENTITY_FACTORY_MAP


# 实体缓存，用于步骤间共享实体
_entity_cache = {}


@given(parsers.parse('存在"{entity_name}":'))
def create_entity_step(entity_name: str, docstring, created_entity: Dict):
    """创建实体步骤（无空格格式）

    示例:
        假如存在"用户":
            {"username": "test", "role": "admin"}
    """
    factory_class = ENTITY_FACTORY_MAP.get(entity_name)
    if not factory_class:
        raise ValueError(f"未知的实体类型: {entity_name}")

    overrides = json.loads(docstring) if docstring else {}
    entity = factory_class(**overrides)

    # 缓存实体，供后续步骤使用
    _entity_cache[entity_name] = entity

    # 更新 created_entity fixture（字典）
    created_entity.clear()
    created_entity.update(
        {
            "entity": entity,
            "id": getattr(entity, "id", None),
            "entity_name": entity_name,
        }
    )


@given(parsers.parse('假如存在"{entity_name}":'))
def create_entity_step_with_prefix(entity_name: str, docstring, created_entity: Dict):
    """创建实体步骤（带假如前缀）"""
    create_entity_step(entity_name, docstring, created_entity)


@given(parsers.parse('存在"{entity_name}"'))
def create_entity_step_simple(entity_name: str, created_entity: Dict):
    """创建实体步骤（无参数）

    示例:
        假如存在"用户"
    """
    factory_class = ENTITY_FACTORY_MAP.get(entity_name)
    if not factory_class:
        raise ValueError(f"未知的实体类型: {entity_name}")

    entity = factory_class()

    # 缓存实体
    _entity_cache[entity_name] = entity

    # 更新 created_entity fixture（字典）
    created_entity.clear()
    created_entity.update(
        {
            "entity": entity,
            "id": getattr(entity, "id", None),
            "entity_name": entity_name,
        }
    )


@given(parsers.parse('假如存在"{entity_name}"'))
def create_entity_step_simple_with_prefix(entity_name: str, created_entity: Dict):
    """创建实体步骤（无参数，带假如前缀）"""
    create_entity_step_simple(entity_name, created_entity)


@given(parsers.parse('系统中存在"{count:d}"个"{entity_name}"'))
def create_multiple_entities_step(count: int, entity_name: str):
    """创建多个实体步骤

    示例:
        系统中存在"5"个"用户"
    """
    factory_class = ENTITY_FACTORY_MAP.get(entity_name)
    if not factory_class:
        raise ValueError(f"未知的实体类型: {entity_name}")

    entities = [factory_class() for _ in range(count)]
    return entities


@given(parsers.parse('数据库中存在"{entity_name}"'))
def verify_entity_in_db(entity_name: str, created_entity: Dict):
    """验证数据库中存在实体"""
    assert created_entity is not None
    assert "id" in created_entity
    assert created_entity["id"] is not None

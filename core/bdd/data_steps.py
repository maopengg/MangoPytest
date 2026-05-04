# -*- coding: utf-8 -*-
"""
通用数据工厂步骤定义

提供跨项目可用的 BDD 步骤：
- 创建命名实体
- 创建多个实体
- 实体属性访问

使用方法:
    1. 在项目 conftest.py 中导入:
       from core.bdd.data_steps import *

    2. 提供 entity_factory_map fixture:
       @pytest.fixture
def entity_factory_map():
           return {
               "用户": UserSpec,
               "产品": ProductSpec,
           }
"""

import pytest
from pytest_bdd import given, parsers

from core.bdd.context import EntityContext
from core.utils import log


@pytest.fixture
def entity_context() -> EntityContext:
    """实体上下文 fixture

    每个测试场景拥有独立的上下文实例。
    """
    return EntityContext()


@given(parsers.parse('存在"{entity_name}" 作为 @{alias}'))
def create_named_entity_step(
    entity_name: str,
    alias: str,
    db_session,
    entity_factory_map: dict,
    entity_context: EntityContext,
):
    """创建命名实体并添加到上下文

    示例:
        假如 存在"产品" 作为 @产品A
        假如 存在"用户" 作为 @买家
    """
    factory_class = entity_factory_map.get(entity_name)
    if not factory_class:
        available = ", ".join(entity_factory_map.keys())
        raise ValueError(f"未知实体类型: '{entity_name}'\n" f"可用实体: {available}")

    log.debug(f"创建实体: {entity_name} 作为 @{alias}")

    # 创建实体（使用 factory_boy 的 create 方法）
    # 设置 sqlalchemy_session
    factory_class._meta.sqlalchemy_session = db_session
    entity = factory_class.create()

    # 添加到上下文
    entity_context.add(alias, entity)

    log.info(
        f"✓ 创建成功: {entity_name} → @{alias} (id={getattr(entity, 'id', 'N/A')})"
    )

    return entity


@given(parsers.parse('存在"{entity_name}"'))
def create_entity_simple_step(
    entity_name: str,
    db_session,
    entity_factory_map: dict,
    entity_context: EntityContext,
):
    """创建实体（使用实体名作为别名）

    示例:
        假如 存在"产品"
        假如 存在"用户"

    会自动将实体名转为小写作为别名，如 "产品" → @产品
    """
    # 使用实体名作为别名（中文）
    alias = entity_name
    return create_named_entity_step(
        entity_name, alias, db_session, entity_factory_map, entity_context
    )


@given(parsers.parse('存在 {count:d} 个"{entity_name}" 作为 @{alias_prefix}'))
def create_multiple_entities_step(
    count: int,
    entity_name: str,
    alias_prefix: str,
    db_session,
    entity_factory_map: dict,
    entity_context: EntityContext,
):
    """创建多个命名实体

    示例:
        假如 存在 3 个"产品" 作为 @产品

    会创建 @产品1, @产品2, @产品3
    """
    factory_class = entity_factory_map.get(entity_name)
    if not factory_class:
        raise ValueError(f"未知实体类型: {entity_name}")

    log.debug(f"批量创建: {count} 个 {entity_name}")

    # 设置 sqlalchemy_session
    factory_class._meta.sqlalchemy_session = db_session

    entities = []
    for i in range(1, count + 1):
        alias = f"{alias_prefix}{i}"
        entity = factory_class.create()
        entity_context.add(alias, entity)
        entities.append(entity)
        log.info(f"✓ 创建成功: {entity_name} → @{alias}")

    return entities


@given(parsers.parse('存在"{entity_name}" 作为 @{alias}:'))
def create_named_entity_with_params_step(
    entity_name: str,
    alias: str,
    docstring: str,
    db_session,
    entity_factory_map: dict,
    entity_context: EntityContext,
):
    """创建命名实体并添加到上下文（支持自定义参数）

    示例:
        假如 存在"用户" 作为 @用户:
          参数 JSON
    """
    import json

    factory_class = entity_factory_map.get(entity_name)
    if not factory_class:
        available = ", ".join(entity_factory_map.keys())
        raise ValueError(f"未知实体类型: '{entity_name}'\n" f"可用实体: {available}")

    log.debug(f"创建实体: {entity_name} 作为 @{alias} (带参数)")

    # 解析自定义参数
    custom_params = {}
    if docstring:
        try:
            custom_params = json.loads(docstring.strip())
        except json.JSONDecodeError as e:
            raise ValueError(f"无效的 JSON 参数: {e}")

    # 设置 sqlalchemy_session
    factory_class._meta.sqlalchemy_session = db_session

    # 创建实体（使用自定义参数）
    entity = factory_class.create(**custom_params)

    # 添加到上下文
    entity_context.add(alias, entity)

    log.info(
        f"✓ 创建成功: {entity_name} → @{alias} (id={getattr(entity, 'id', 'N/A')})"
    )

    return entity

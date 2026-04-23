# -*- coding: utf-8 -*-
"""
数据准备步骤

提供使用 factory_boy 创建测试数据的步骤定义
"""

from auto_tests.bdd_api_mock.steps.data.factory import (
    create_entity_step,
    create_entity_step_with_prefix,
    create_entity_step_simple,
    create_entity_step_simple_with_prefix,
    create_multiple_entities_step,
    verify_entity_in_db,
)

__all__ = [
    "create_entity_step",
    "create_entity_step_with_prefix",
    "create_entity_step_simple",
    "create_entity_step_simple_with_prefix",
    "create_multiple_entities_step",
    "verify_entity_in_db",
]

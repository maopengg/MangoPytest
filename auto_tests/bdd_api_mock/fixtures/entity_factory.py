# -*- coding: utf-8 -*-
"""
实体工厂 Fixtures

直接使用 data_factory.specs 中定义的 ENTITY_FACTORY_MAP
"""

import pytest


@pytest.fixture(scope="session")
def entity_factory_map():
    """实体工厂映射

    将中文实体名映射到对应的 Factory 类
    从 data_factory.specs 导入，避免重复定义
    """
    from auto_tests.bdd_api_mock.data_factory.specs import ENTITY_FACTORY_MAP
    return ENTITY_FACTORY_MAP

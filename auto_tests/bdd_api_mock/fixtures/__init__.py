# -*- coding: utf-8 -*-
"""
Fixture 模块包

包含项目特定的 fixtures：
- clients: API 客户端
- entity_factory: 实体工厂映射
"""

from auto_tests.bdd_api_mock.fixtures.clients import (
    mock_api_settings,
    api_client,
    json_client,
    form_client,
    multipart_client,
    db_session,
)
from auto_tests.bdd_api_mock.fixtures.entity_factory import entity_factory_map

__all__ = [
    "mock_api_settings",
    "api_client",
    "json_client",
    "form_client",
    "multipart_client",
    "db_session",
    "entity_factory_map",
]

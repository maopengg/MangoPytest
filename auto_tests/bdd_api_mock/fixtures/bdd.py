# -*- coding: utf-8 -*-
"""BDD 公共 Fixtures"""
import pytest


@pytest.fixture
def api_response():
    """API 响应 fixture，用于步骤间共享 API 响应数据"""
    return {}


@pytest.fixture
def created_entity():
    """当前创建的实体 fixture，用于步骤间共享实体数据"""
    return {}

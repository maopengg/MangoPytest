# -*- coding: utf-8 -*-
"""
通用步骤和 Fixtures

提供测试步骤间共享的基础 fixtures
"""

import pytest
from typing import Any, Dict


@pytest.fixture
def api_response():
    """API 响应 fixture

    用于在步骤间共享 API 响应数据
    """
    return {}


@pytest.fixture
def created_entity():
    """当前创建的实体 fixture

    用于在步骤间共享实体数据。返回一个字典，可以存储和更新实体。
    """
    return {}

# -*- coding: utf-8 -*-
"""UI 配置 Fixtures"""
import pytest


@pytest.fixture(scope="session")
def ui_config():
    """UI 配置 fixture"""
    from auto_tests.bdd_ui_mock.config import settings
    return settings

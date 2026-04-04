# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 系统模块 fixtures
# @Time   : 2026-03-31
# @Author : 毛鹏
from typing import Generator, Dict, Any

import pytest

from auto_test.demo_project.data_factory.builders.system import SystemBuilder


@pytest.fixture(scope="function")
def system_builder(test_token) -> SystemBuilder:
    """系统构造器 fixture"""
    return SystemBuilder(token=test_token)


@pytest.fixture(scope="function")
def server_health(system_builder) -> Generator[Dict[str, Any], None, None]:
    """
    服务器健康状态 fixture
    检查服务器健康状态
    """
    health = system_builder.health_check()
    if not health:
        pytest.skip("无法获取服务器健康状态")

    yield health


@pytest.fixture(scope="function")
def server_info(system_builder) -> Generator[Dict[str, Any], None, None]:
    """
    服务器信息 fixture
    获取服务器信息
    """
    info = system_builder.get_server_info()
    if not info:
        pytest.skip("无法获取服务器信息")

    yield info

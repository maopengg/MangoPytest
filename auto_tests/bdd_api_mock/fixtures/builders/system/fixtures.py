# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 系统模块 fixtures
# @Time   : 2026-03-31
# @Author : 毛鹏
from typing import Generator, Dict, Any

import pytest

from auto_tests.bdd_api_mock.data_factory.builders.system import SystemBuilder


@pytest.fixture(scope="session")
def system_builder() -> SystemBuilder:
    """系统构造器 fixture"""
    return SystemBuilder()


@pytest.fixture
def system_status(system_builder) -> Dict[str, Any]:
    """
    系统状态 fixture
    获取系统当前状态
    """
    status = system_builder.get_status()
    return status


@pytest.fixture
def system_config(system_builder) -> Dict[str, Any]:
    """
    系统配置 fixture
    获取系统配置信息
    """
    config = system_builder.get_config()
    return config


@pytest.fixture
def server_health(system_builder) -> Dict[str, Any]:
    """
    服务器健康检查 fixture
    获取服务器健康状态
    """
    return system_builder.health_check()


@pytest.fixture
def server_info(system_builder) -> Dict[str, Any]:
    """
    服务器信息 fixture
    获取服务器信息
    """
    return system_builder.get_server_info()

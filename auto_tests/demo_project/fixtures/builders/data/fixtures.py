# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 数据模块 fixtures
# @Time   : 2026-03-31
# @Author : 毛鹏
from typing import Generator, Dict, Any

import pytest

from auto_tests.demo_project.data_factory.builders.data import DataBuilder


@pytest.fixture(scope="function")
def data_builder(authenticated_client) -> Generator[DataBuilder, None, None]:
    """
    数据构造器 fixture
    提供DataBuilder实例用于创建和管理数据
    """
    builder = DataBuilder(token=authenticated_client.token)
    yield builder
    # 清理创建的数据
    builder.cleanup()


@pytest.fixture
def test_data(data_builder) -> Dict[str, Any]:
    """
    测试数据 fixture
    创建一条测试数据
    """
    data = data_builder.create()
    return data


@pytest.fixture
def data_list(data_builder) -> list:
    """
    数据列表 fixture
    创建多条测试数据
    """
    data_list = data_builder.create_batch(5)
    return data_list


@pytest.fixture
def submitted_data(data_builder) -> Dict[str, Any]:
    """
    已提交数据 fixture
    创建一条已提交的数据，使用特定名称以匹配测试期望
    """
    data = data_builder.create_submitted(name="test_data", value=100)
    return data

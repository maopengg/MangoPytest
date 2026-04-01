# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 数据模块 fixtures
# @Time   : 2026-03-31
# @Author : 毛鹏
import pytest
from typing import Generator, Dict, Any

from auto_test.demo_project.data_factory.builders.data import DataBuilder


@pytest.fixture(scope="function")
def data_builder(test_token) -> DataBuilder:
    """数据构造器 fixture"""
    return DataBuilder(token=test_token)


@pytest.fixture(scope="function")
def submitted_data(data_builder) -> Generator[Dict[str, Any], None, None]:
    """
    已提交数据 fixture
    提交测试数据并返回结果
    """
    result = data_builder.submit(name="test_data", value=100)
    if not result:
        pytest.skip("无法提交测试数据")
    
    yield result

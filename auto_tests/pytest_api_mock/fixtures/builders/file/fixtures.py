# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 文件模块 fixtures
# @Time   : 2026-03-31
# @Author : 毛鹏
from typing import Generator, Dict, Any

import pytest

from auto_tests.pytest_api_mock.data_factory.builders.file import FileBuilder


@pytest.fixture(scope="function")
def file_builder(authenticated_client) -> Generator[FileBuilder, None, None]:
    """
    文件构造器 fixture
    提供FileBuilder实例用于创建和管理文件
    """
    builder = FileBuilder(token=authenticated_client.token)
    yield builder
    # 清理创建的数据
    builder.cleanup()


@pytest.fixture
def uploaded_file(file_builder) -> Dict[str, Any]:
    """
    已上传文件 fixture
    上传一个测试文件
    """
    file = file_builder.upload(filename="测试上传文件.txt", content="测试文件内容")
    return file


@pytest.fixture
def file_list(file_builder) -> list:
    """
    文件列表 fixture
    上传多个测试文件
    """
    files = file_builder.upload_batch(3)
    return files


@pytest.fixture
def temp_file(file_builder) -> str:
    """
    临时文件 fixture
    创建一个临时文件用于测试，返回文件路径
    使用特定文件名 "测试上传文件.txt" 以匹配测试期望
    """
    file_info = file_builder.create_temp_file(filename="测试上传文件.txt", content="测试文件内容")
    # 返回文件路径字符串
    return file_info["path"] if isinstance(file_info, dict) else file_info

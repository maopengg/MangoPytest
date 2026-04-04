# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 文件模块 fixtures
# @Time   : 2026-03-31
# @Author : 毛鹏
from typing import Generator, Dict, Any

import pytest

from auto_tests.demo_project.data_factory.builders.file import FileBuilder


@pytest.fixture(scope="function")
def file_builder(test_token) -> FileBuilder:
    """文件构造器 fixture"""
    return FileBuilder(token=test_token)


@pytest.fixture(scope="function")
def temp_file() -> Generator[str, None, None]:
    """
    临时文件 fixture
    使用项目内固定测试文件路径
    """
    file_path = r"D:\code\MangoPytest\auto_test\demo_project\data\uploads\测试上传文件.txt"

    yield file_path


@pytest.fixture(scope="function")
def uploaded_file(file_builder, temp_file) -> Generator[Dict[str, Any], None, None]:
    """
    已上传文件 fixture
    上传临时文件并返回结果
    """
    result = file_builder.upload(file_path=temp_file)
    if not result:
        pytest.skip("无法上传测试文件")

    yield result

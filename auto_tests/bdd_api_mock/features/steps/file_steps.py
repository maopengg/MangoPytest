# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 文件管理模块 BDD 步骤定义
# @Time   : 2026-04-17
# @Author : 毛鹏
"""
文件管理模块步骤定义
"""

import os
import tempfile
import pytest
from pytest_bdd import given, when, then, parsers
from pytest_bdd.parsers import parse

from auto_tests.bdd_api_mock.data_factory.builders.file import FileBuilder


# ==================== Given 步骤 ====================


@given(
    parsers.parse('用户准备了测试文件 "{filename}"'), target_fixture="test_file_path"
)
def prepare_test_file(filename):
    """准备测试文件"""
    # 使用项目中的测试文件
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    file_path = os.path.join(base_dir, "data", "uploads", filename)
    return file_path


@given("系统已创建临时文件", target_fixture="temp_file_path")
def create_temp_file(authenticated_user):
    """创建临时文件"""
    token = authenticated_user["token"]
    file_builder = FileBuilder(token=token)
    file_path = file_builder.build_temp_file(filename="测试上传文件.txt")
    return file_path


# ==================== When 步骤 ====================


@when("用户上传该文件", target_fixture="upload_result")
def user_upload_file(authenticated_user, test_file_path):
    """用户上传文件"""
    token = authenticated_user["token"]
    file_builder = FileBuilder(token=token)
    result = file_builder.upload(file_path=test_file_path)
    return result


@when("用户上传空内容文件", target_fixture="upload_result")
def user_upload_empty_file(authenticated_user):
    """用户上传空内容文件"""
    token = authenticated_user["token"]
    file_builder = FileBuilder(token=token)
    result = file_builder.upload(content="")
    return result


@when(
    parsers.parse("用户上传大内容文件，大小为 {size:d} 字节"),
    target_fixture="upload_result",
)
def user_upload_large_file(authenticated_user, size):
    """用户上传大内容文件"""
    token = authenticated_user["token"]
    file_builder = FileBuilder(token=token)
    large_content = "A" * size
    result = file_builder.upload(content=large_content)
    return result


@when(
    parsers.parse('用户上传文件，文件名为 "{filename}"'), target_fixture="upload_result"
)
def user_upload_with_filename(authenticated_user, filename):
    """用户上传指定文件名的文件"""
    token = authenticated_user["token"]
    file_builder = FileBuilder(token=token)
    result = file_builder.upload(filename=filename, content="test content")
    return result


@when("用户使用该临时文件上传", target_fixture="upload_result")
def user_upload_with_temp_file(authenticated_user, temp_file_path):
    """用户使用临时文件上传"""
    token = authenticated_user["token"]
    file_builder = FileBuilder(token=token)
    result = file_builder.upload(file_path=temp_file_path)
    return result


@when("用户上传以下格式的文件:", target_fixture="upload_results")
def user_upload_multiple_files(authenticated_user, table):
    """用户上传多个文件"""
    token = authenticated_user["token"]
    file_builder = FileBuilder(token=token)
    results = []

    for row in table:
        result = file_builder.upload(filename=row["filename"], content=row["content"])
        results.append(result)

    return results


# ==================== Then 步骤 ====================


@then("文件应该上传成功")
def verify_file_uploaded(upload_result):
    """验证文件上传成功"""
    assert upload_result is not None


@then(parsers.parse('返回的文件名应该是 "{filename}"'))
def verify_uploaded_filename(upload_result, filename):
    """验证返回的文件名"""
    assert upload_result.get("filename") == filename


@then("返回的文件大小应该大于等于 0")
def verify_file_size_non_negative(upload_result):
    """验证文件大小非负"""
    assert upload_result.get("size") >= 0


@then("返回的文件应该包含有效的文件ID")
def verify_file_has_id(upload_result):
    """验证文件包含有效ID"""
    assert "file_id" in upload_result
    assert upload_result["file_id"] is not None


@then(parsers.parse("文件大小应该大于等于 {size:d}"))
def verify_file_size_gte(upload_result, size):
    """验证文件大小大于等于指定值"""
    assert upload_result.get("size") >= size


@then(parsers.parse("文件大小应该大于 {size:d}"))
def verify_file_size_gt(upload_result, size):
    """验证文件大小大于指定值"""
    assert upload_result.get("size") > size


@then("所有文件都应该上传成功")
def verify_all_files_uploaded(upload_results):
    """验证所有文件都上传成功"""
    for result in upload_results:
        assert result is not None

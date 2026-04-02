# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 文件上传测试用例 - /upload
# @Time   : 2026-03-31
# @Author : 毛鹏
import pytest
import allure
import os

from auto_test.demo_project.data_factory.builders.file import FileBuilder
from auto_test.demo_project.fixtures.conftest import *
from auto_test.demo_project.test_cases.base import UnitTest


@allure.feature("文件管理")
@allure.story("文件上传")
class TestUploadFile(UnitTest):
    """文件上传接口测试"""

    SAMPLE_UPLOAD_FILE = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "data",
        "uploads",
        "测试上传文件.txt",
    )

    @allure.title("正常上传文件")
    def test_upload_file_success(self, test_token):
        """测试正常上传文件"""
        file_builder = FileBuilder(token=test_token)

        result = file_builder.upload(file_path=self.SAMPLE_UPLOAD_FILE)

        assert result is not None
        assert result.get('filename') == "测试上传文件.txt"
        assert result.get('size') >= 0
        assert 'file_id' in result

    @allure.title("上传文件-使用fixture")
    def test_upload_file_with_fixture(self, uploaded_file):
        """测试使用fixture上传的文件"""
        assert uploaded_file is not None
        assert uploaded_file.get('filename') == "测试上传文件.txt"
        assert uploaded_file.get('size') >= 0
        assert 'file_id' in uploaded_file

    @allure.title("上传文件-不同内容类型")
    def test_upload_different_content(self, test_token):
        """测试上传不同内容的文件"""
        file_builder = FileBuilder(token=test_token)
        
        # 上传空文件
        result1 = file_builder.upload(content="")
        assert result1 is not None
        assert result1.get('size') >= 0  # 空文件大小可能为0或包含一些元数据
        
        # 上传大内容文件
        large_content = "A" * 10000
        result2 = file_builder.upload(content=large_content)
        assert result2 is not None
        assert result2.get('size') > 0  # 大文件应该有大小

    @allure.title("上传文件-不同文件名")
    def test_upload_different_filenames(self, test_token):
        """测试上传不同文件名的文件"""
        file_builder = FileBuilder(token=test_token)
        
        # 中文文件名
        result1 = file_builder.upload(filename="中文文件.txt", content="content")
        assert result1 is not None
        
        # 包含空格的文件名
        result2 = file_builder.upload(filename="file with spaces.txt", content="content")
        assert result2 is not None
        
        # 特殊扩展名
        result3 = file_builder.upload(filename="test.pdf", content="PDF content")
        assert result3 is not None
        
        # JSON文件
        result4 = file_builder.upload(filename="data.json", content='{"key": "value"}')
        assert result4 is not None

    @allure.title("上传文件-使用temp_file fixture")
    def test_upload_with_temp_file_fixture(self, test_token, temp_file):
        """测试使用temp_file fixture上传"""
        file_builder = FileBuilder(token=test_token)
        result = file_builder.upload(file_path=temp_file)

        assert result is not None
        assert result.get('filename') == "测试上传文件.txt"
        # content_type 可能为 None，取决于 mock API 的实现
        assert 'content_type' in result

    @allure.title("创建临时文件-使用数据工厂")
    def test_create_temp_file_with_builder(self, test_token):
        """测试使用数据工厂创建临时文件"""
        file_builder = FileBuilder(token=test_token)
        
        # 使用build_temp_file创建临时文件
        file_path = file_builder.build_temp_file(
            content="Test content from builder",
            filename="builder_test.txt"
        )
        
        assert os.path.exists(file_path)
        assert os.path.basename(file_path) == "builder_test.txt"
        
        # 读取内容验证
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        assert content == "Test content from builder"
        
        # 清理
        os.remove(file_path)

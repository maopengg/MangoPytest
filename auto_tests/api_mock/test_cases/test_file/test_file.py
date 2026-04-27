# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 文件上传测试 - 不依赖Excel，直接调用Mock API
# @Time   : 2026-04-25
# @Author : 毛鹏

import allure
import pytest
import os
import tempfile

from auto_tests.api_mock import user_info, BASE_URL
from core.api.client import APIClient


@allure.epic('演示-API自动化-常规API-MockAPI服务')
@allure.feature('文件上传模块')
class TestFile:
    """文件上传测试类 - 直接调用Mock API，不依赖Excel"""

    @pytest.fixture(scope="class")
    def api_client_with_token(self):
        """创建API客户端并登录获取token，返回client和headers"""
        client = APIClient(base_url=BASE_URL)

        # 登录获取token
        response = client.post("/auth/login", json={
            "username": user_info["username"],
            "password": user_info["password"]
        })

        if response.data.get("code") == 200:
            token = response.data["data"]["token"]
            headers = {
                "X-Token": token,
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            return client, headers
        else:
            pytest.skip("登录失败，跳过测试")

    @pytest.fixture
    def create_test_file(self):
        """创建测试文件，返回文件路径"""
        # 创建临时文件
        fd, file_path = tempfile.mkstemp(suffix='.txt', prefix='test_upload_')
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                f.write("这是一个测试文件内容\n")
                f.write("用于测试文件上传接口\n")
            yield file_path
        finally:
            # 清理临时文件
            if os.path.exists(file_path):
                os.remove(file_path)

    @pytest.fixture
    def create_test_image_file(self):
        """创建一个简单的测试图片文件"""
        fd, file_path = tempfile.mkstemp(suffix='.jpg', prefix='test_image_')
        try:
            # 写入简单的JPEG文件头（假的JPEG文件，仅用于测试）
            with os.fdopen(fd, 'wb') as f:
                # JPEG文件头
                f.write(b'\xff\xd8\xff\xe0\x00\x10JFIF')
                f.write(b'\x00' * 100)  # 填充数据
            yield file_path
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)

    @allure.story("文件上传")
    @allure.title("上传文本文件成功")
    def test_upload_text_file(self, api_client_with_token, create_test_file):
        """测试上传文本文件"""
        client, headers = api_client_with_token

        # 移除Content-Type让httpx自动设置
        upload_headers = {
            "X-Token": headers["X-Token"],
            "Authorization": headers["Authorization"]
        }

        response = client.upload("/upload", file_path=create_test_file, headers=upload_headers)

        assert response.data.get("code") == 200
        assert response.data.get("message") == "上传成功"
        assert "filename" in response.data["data"]
        assert "content_type" in response.data["data"]
        assert "size" in response.data["data"]
        assert "file_id" in response.data["data"]

    @allure.story("文件上传")
    @allure.title("上传图片文件成功")
    def test_upload_image_file(self, api_client_with_token, create_test_image_file):
        """测试上传图片文件"""
        client, headers = api_client_with_token

        upload_headers = {
            "X-Token": headers["X-Token"],
            "Authorization": headers["Authorization"]
        }

        response = client.upload("/upload", file_path=create_test_image_file, headers=upload_headers)

        assert response.data.get("code") == 200
        assert "filename" in response.data["data"]

    @allure.story("文件上传")
    @allure.title("上传文件-未授权访问失败")
    def test_upload_without_token(self, create_test_file):
        """测试未授权上传文件"""
        client = APIClient(base_url=BASE_URL)

        from core.exceptions import ApiError
        with pytest.raises(ApiError) as exc_info:
            client.upload("/upload", file_path=create_test_file)

        # 应该返回401未授权错误
        assert "401" in str(exc_info.value)

    @allure.story("文件上传")
    @allure.title("上传文件带额外数据")
    def test_upload_with_extra_data(self, api_client_with_token, create_test_file):
        """测试上传文件时携带额外表单数据"""
        client, headers = api_client_with_token

        upload_headers = {
            "X-Token": headers["X-Token"],
            "Authorization": headers["Authorization"]
        }

        extra_data = {"folder": "test_folder", "description": "测试文件"}
        response = client.upload("/upload", file_path=create_test_file, data=extra_data, headers=upload_headers)

        assert response.data.get("code") == 200
        assert response.data.get("message") == "上传成功"


if __name__ == '__main__':
    pytest.main(['-v', __file__])

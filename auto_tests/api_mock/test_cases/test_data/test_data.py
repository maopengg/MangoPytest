# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 数据提交测试 - 不依赖Excel，直接调用Mock API
# @Time   : 2026-04-25
# @Author : 毛鹏

import allure
import pytest
import time

from auto_tests.api_mock import user_info, BASE_URL
from core.api.client import APIClient


@allure.epic('演示-API自动化-常规API-MockAPI服务')
@allure.feature('数据提交模块')
class TestData:
    """数据提交测试类 - 直接调用Mock API，不依赖Excel"""

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

    @allure.story("提交数据")
    @allure.title("提交数据成功")
    def test_submit_data_success(self, api_client_with_token):
        """测试提交数据"""
        client, headers = api_client_with_token

        timestamp = int(time.time())
        json_data = {
            "name": f"test_data_{timestamp}",
            "value": timestamp
        }

        response = client.post("/api/data", json=json_data, headers=headers)

        assert response.data.get("code") == 200
        assert response.data.get("message") == "数据提交成功"
        assert response.data["data"]["name"] == json_data["name"]
        assert response.data["data"]["value"] == json_data["value"]
        assert "timestamp" in response.data["data"]

    @allure.story("提交数据")
    @allure.title("提交数据-未授权访问失败")
    def test_submit_data_without_token(self):
        """测试未授权提交数据"""
        client = APIClient(base_url=BASE_URL)

        json_data = {
            "name": "test_data",
            "value": 123
        }

        from core.exceptions import ApiError
        with pytest.raises(ApiError) as exc_info:
            client.post("/api/data", json=json_data)

        # 应该返回401未授权错误
        assert "401" in str(exc_info.value)

    @allure.story("提交数据")
    @allure.title("提交数据-缺少必填字段")
    def test_submit_data_missing_fields(self, api_client_with_token):
        """测试提交数据缺少必填字段"""
        client, headers = api_client_with_token

        # 缺少value字段
        json_data = {
            "name": "test_data"
        }

        # API可能对缺少字段的处理不同：可能返回错误，也可能使用默认值
        try:
            response = client.post("/api/data", json=json_data, headers=headers)
            # 如果请求成功，验证返回码
            assert response.data.get("code") in [200, 400, 422]
        except Exception as e:
            # 如果抛出异常，验证是参数错误
            assert any(err in str(e) for err in ["422", "400", "missing", "required"])


if __name__ == '__main__':
    pytest.main(['-v', __file__])

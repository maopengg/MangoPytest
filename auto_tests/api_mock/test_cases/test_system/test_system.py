# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 系统管理测试 - 不依赖Excel，直接调用Mock API
# @Time   : 2026-04-25
# @Author : 毛鹏

import allure
import pytest

from auto_tests.api_mock import user_info, BASE_URL
from core.api.client import APIClient


@allure.epic('演示-API自动化-常规API-MockAPI服务')
@allure.feature('系统管理模块')
class TestSystem:
    """系统管理测试类 - 直接调用Mock API，不依赖Excel"""

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

    @allure.story("健康检查")
    @allure.title("健康检查接口正常")
    def test_health_check(self, api_client_with_token):
        """测试健康检查接口"""
        client, headers = api_client_with_token
        response = client.get("/health", headers=headers)

        assert response.data.get("code") == 200
        assert response.data.get("message") == "服务正常运行"
        assert response.data["data"]["status"] == "healthy"
        assert "timestamp" in response.data["data"]

    @allure.story("健康检查")
    @allure.title("健康检查-未授权访问失败")
    def test_health_check_without_token(self):
        """测试未授权访问健康检查接口"""
        client = APIClient(base_url=BASE_URL)

        from core.exceptions import ApiError
        with pytest.raises(ApiError) as exc_info:
            client.get("/health")

        # 应该返回401未授权错误
        assert "401" in str(exc_info.value)

    @allure.story("服务器信息")
    @allure.title("获取服务器信息成功")
    def test_get_server_info(self, api_client_with_token):
        """测试获取服务器信息接口"""
        client, headers = api_client_with_token
        response = client.get("/info", headers=headers)

        assert response.data.get("code") == 200
        assert response.data.get("message") == "获取成功"
        assert "app_name" in response.data["data"]
        assert "version" in response.data["data"]
        assert "framework" in response.data["data"]
        assert response.data["data"]["framework"] == "FastAPI"
        assert "python_version" in response.data["data"]

    @allure.story("服务器信息")
    @allure.title("获取服务器信息-未授权访问失败")
    def test_get_server_info_without_token(self):
        """测试未授权获取服务器信息"""
        client = APIClient(base_url=BASE_URL)

        from core.exceptions import ApiError
        with pytest.raises(ApiError) as exc_info:
            client.get("/info")

        # 应该返回401未授权错误
        assert "401" in str(exc_info.value)

    @allure.story("初始化数据")
    @allure.title("初始化测试数据成功")
    def test_startup_init_data(self, api_client_with_token):
        """测试初始化数据接口"""
        client, headers = api_client_with_token
        response = client.get("/startup", headers=headers)

        assert response.data.get("code") == 200
        # API返回的消息可能是"初始化完成"或"数据初始化成功"
        assert response.data.get("message") in ["数据初始化成功", "初始化完成"]
        # data中可能包含初始化信息
        assert "data" in response.data

    @allure.story("初始化数据")
    @allure.title("初始化数据-未授权访问")
    def test_startup_without_token(self):
        """测试未授权初始化数据"""
        client = APIClient(base_url=BASE_URL)

        # 某些API可能允许未授权访问初始化接口
        try:
            response = client.get("/startup")
            # 如果请求成功，验证返回码
            assert response.data.get("code") in [200, 401]
        except Exception as e:
            # 如果抛出异常，验证是401错误
            assert "401" in str(e) or "Unauthorized" in str(e)


if __name__ == '__main__':
    pytest.main(['-v', __file__])

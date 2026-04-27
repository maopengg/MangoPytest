# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 用户管理测试 - 不依赖Excel，直接调用Mock API
# @Time   : 2026-01-18 14:05
# @Author : 毛鹏

import allure
import pytest
import hashlib
import time

from auto_tests.api_mock import user_info
from core.api.client import APIClient


@allure.epic('演示-API自动化-常规API-MockAPI服务')
@allure.feature('用户管理模块')
class TestUser:
    """用户管理测试类 - 直接调用Mock API，不依赖Excel"""

    @pytest.fixture(scope="class")
    def api_client_with_token(self):
        """创建API客户端并登录获取token，返回client和headers"""
        client = APIClient(base_url="http://43.142.161.61:8003")
        
        # 登录获取token - user_info中的密码已经是MD5格式
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

    @allure.story("获取用户列表")
    @allure.title("获取所有用户列表")
    def test_get_all_users(self, api_client_with_token):
        """测试获取所有用户列表"""
        client, headers = api_client_with_token
        response = client.get("/users", headers=headers)
        
        assert response.data.get("code") == 200
        assert response.data.get("message") == "获取成功"
        assert isinstance(response.data.get("data"), list)

    @allure.story("获取用户详情")
    @allure.title("根据ID获取用户详情")
    def test_get_user_by_id(self, api_client_with_token):
        """测试根据ID获取用户详情"""
        client, headers = api_client_with_token
        
        # 先获取用户列表
        response = client.get("/users", headers=headers)
        users = response.data.get("data", [])
        
        if not users:
            pytest.skip("没有用户数据，跳过测试")
        
        user_id = users[0]["id"]
        
        # 根据ID获取用户
        response = client.get("/users", params={"id": user_id}, headers=headers)
        
        assert response.data.get("code") == 200
        assert response.data.get("data")["id"] == user_id

    @allure.story("获取用户详情")
    @allure.title("获取不存在的用户")
    def test_get_user_not_found(self, api_client_with_token):
        """测试获取不存在的用户"""
        client, headers = api_client_with_token
        response = client.get("/users", params={"id": 99999}, headers=headers)
        
        assert response.data.get("code") == 404
        assert "不存在" in response.data.get("message", "")

    @allure.story("更新用户信息")
    @allure.title("更新用户信息成功")
    def test_update_user_success(self, api_client_with_token):
        """测试更新用户信息"""
        client, headers = api_client_with_token
        
        # 先获取用户列表
        response = client.get("/users", headers=headers)
        users = response.data.get("data", [])
        
        if not users:
            pytest.skip("没有用户数据，跳过测试")
        
        user_id = users[0]["id"]
        
        # 更新用户
        update_data = {
            "username": users[0]["username"],
            "email": "updated@example.com",
            "full_name": "Updated Name",
            "role": users[0].get("role", "user"),
            "password": "password123"  # 需要传递，但API不会更新
        }
        response = client.put(f"/users/{user_id}", json=update_data, headers=headers)
        
        assert response.data.get("code") == 200
        assert response.data.get("data")["email"] == "updated@example.com"

    @allure.story("更新用户信息")
    @allure.title("更新不存在的用户")
    def test_update_user_not_found(self, api_client_with_token):
        """测试更新不存在的用户"""
        client, headers = api_client_with_token
        
        update_data = {
            "username": "testuser",
            "email": "test@example.com",
            "full_name": "Test User",
            "role": "user",
            "password": "password123"
        }
        response = client.put("/users/99999", json=update_data, headers=headers)
        
        assert response.data.get("code") == 404

    @allure.story("删除用户")
    @allure.title("删除用户成功")
    def test_delete_user_success(self, api_client_with_token):
        """测试删除用户"""
        client, headers = api_client_with_token
        
        # 先创建一个新用户
        password_md5 = hashlib.md5("password123".encode()).hexdigest()
        create_response = client.post("/auth/register", json={
            "username": f"testuser_{int(time.time())}",
            "email": "test@example.com",
            "full_name": "Test User",
            "password": password_md5
        })
        
        if create_response.data.get("code") != 200:
            pytest.skip("创建用户失败，跳过测试")
        
        # 获取用户列表找到刚创建的用户
        response = client.get("/users", headers=headers)
        users = response.data.get("data", [])
        
        # 找到刚创建的用户（通过用户名）
        created_user = None
        for user in users:
            if user.get("email") == "test@example.com":
                created_user = user
                break
        
        if not created_user:
            pytest.skip("未找到刚创建的用户，跳过测试")
        
        user_id = created_user["id"]
        
        # 删除用户
        response = client.delete(f"/users/{user_id}", headers=headers)
        
        assert response.data.get("code") == 200
        assert "删除成功" in response.data.get("message", "")

    @allure.story("删除用户")
    @allure.title("删除不存在的用户")
    def test_delete_user_not_found(self, api_client_with_token):
        """测试删除不存在的用户"""
        client, headers = api_client_with_token
        response = client.delete("/users/99999", headers=headers)
        
        assert response.data.get("code") == 404
        assert "不存在" in response.data.get("message", "")


if __name__ == '__main__':
    pytest.main(['-v', __file__])

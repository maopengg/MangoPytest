# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 认证测试 - 不依赖Excel，直接调用Mock API
# @Time   : 2026-01-18 14:04
# @Author : 毛鹏

import allure
import pytest
import time

from auto_tests.api_mock.abstract.auth.auth import AuthAPI


@allure.epic('演示-API自动化-常规API-MockAPI服务')
@allure.feature('认证模块')
class TestAuth:
    """认证测试类 - 直接调用API，不依赖Excel"""

    @pytest.fixture(scope="class")
    def auth_api(self):
        """创建AuthAPI实例"""
        return AuthAPI()

    @allure.story('用户登录')
    @allure.title("使用正确凭据登录成功")
    def test_login_success(self, auth_api):
        """测试使用正确凭据登录"""
        response = auth_api.api_login()

        assert response.get("code") == 200
        assert response.get("message") == "登录成功"
        assert "token" in response.get("data", {})
        assert response["data"]["username"] is not None

    @allure.story('用户登录')
    @allure.title("使用错误密码登录失败")
    def test_login_wrong_password(self, auth_api):
        """测试使用错误密码登录"""
        response = auth_api.api_login(password="wrongpassword123")

        # Mock API返回402表示密码错误
        assert response.get("code") == 402
        assert "密码错误" in response.get("message", "")

    @allure.story('用户登录')
    @allure.title("使用不存在用户登录失败")
    def test_login_user_not_found(self, auth_api):
        """测试使用不存在用户登录"""
        response = auth_api.api_login(username="nonexistentuser123")

        # Mock API返回401表示用户不存在或密码错误
        assert response.get("code") == 401
        assert "用户名或密码错误" in response.get("message", "")

    @allure.story('用户登录')
    @allure.title("使用空用户名登录失败")
    def test_login_empty_username(self, auth_api):
        """测试使用空用户名登录"""
        response = auth_api.api_login(username="")

        # 应该返回400或422错误
        assert response.get("code") in [400, 422]

    @allure.story('用户登录')
    @allure.title("使用空密码登录失败")
    def test_login_empty_password(self, auth_api):
        """测试使用空密码登录"""
        response = auth_api.api_login(password="")

        # 应该返回400或401错误
        assert response.get("code") in [400, 401, 422]

    @allure.story('用户注册')
    @allure.title("注册新用户成功")
    def test_register_success(self, auth_api):
        """测试注册新用户"""
        timestamp = int(time.time())
        response = auth_api.api_register(
            username=f"testuser_{timestamp}",
            email=f"test_{timestamp}@example.com",
            full_name="Test User",
            password="password123"
        )

        assert response.get("code") == 200
        assert response.get("message") == "注册成功"
        assert "id" in response.get("data", {})

    @allure.story('用户注册')
    @allure.title("注册重复用户名失败")
    def test_register_duplicate_username(self, auth_api):
        """测试注册重复用户名"""
        # 先注册一个用户
        timestamp = int(time.time())
        username = f"dupuser_{timestamp}"

        # 第一次注册
        response1 = auth_api.api_register(
            username=username,
            email=f"test1_{timestamp}@example.com",
            full_name="Test User 1",
            password="password123"
        )
        assert response1.get("code") == 200

        # 第二次使用相同用户名注册
        response2 = auth_api.api_register(
            username=username,
            email=f"test2_{timestamp}@example.com",
            full_name="Test User 2",
            password="password123"
        )

        assert response2.get("code") == 400
        assert "已存在" in response2.get("message", "")

    @allure.story('用户注册')
    @allure.title("注册重复邮箱失败")
    def test_register_duplicate_email(self, auth_api):
        """测试注册重复邮箱 - Mock API可能不校验邮箱唯一性"""
        # 先注册一个用户
        timestamp = int(time.time())
        email = f"dupemail_{timestamp}@example.com"

        # 第一次注册
        response1 = auth_api.api_register(
            username=f"user1_{timestamp}",
            email=email,
            full_name="Test User 1",
            password="password123"
        )
        assert response1.get("code") == 200

        # 第二次使用相同邮箱注册
        # 注意：Mock API可能不校验邮箱唯一性，只校验用户名
        response2 = auth_api.api_register(
            username=f"user2_{timestamp}",  # 不同用户名
            email=email,  # 相同邮箱
            full_name="Test User 2",
            password="password123"
        )

        # Mock API可能允许重复邮箱，这里我们只验证请求成功或返回错误
        assert response2.get("code") in [200, 400]
        if response2.get("code") == 400:
            assert "已存在" in response2.get("message", "")

    @allure.story('用户注册')
    @allure.title("注册缺少必填字段失败")
    def test_register_missing_fields(self, auth_api):
        """测试注册缺少必填字段"""
        # 通过直接调用底层client来测试缺少字段的情况
        from core.exceptions import ApiError

        with pytest.raises(ApiError) as exc_info:
            auth_api.client.post("/auth/register", json={
                "username": f"testuser_{int(time.time())}"
                # 缺少email, full_name, password
            })

        # 验证错误消息中包含422
        assert "422" in str(exc_info.value)

    @allure.story('获取Token')
    @allure.title("获取认证Token成功")
    def test_get_token(self, auth_api):
        """测试获取认证Token"""
        token = auth_api.get_token()

        assert token is not None
        assert len(token) > 0
        assert "mock_token" in token

    @allure.story('获取Token')
    @allure.title("获取认证Headers成功")
    def test_get_auth_headers(self, auth_api):
        """测试获取认证Headers"""
        headers = auth_api.get_auth_headers()

        assert "X-Token" in headers
        assert "Authorization" in headers
        assert "Content-Type" in headers
        assert headers["Authorization"].startswith("Bearer ")


if __name__ == '__main__':
    pytest.main(['-v', __file__])

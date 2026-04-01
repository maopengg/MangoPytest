# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 认证模块测试用例 - /auth/login, /auth/register
# @Time   : 2026-03-31
# @Author : 毛鹏
import pytest
import allure

from auto_test.demo_project.data_factory.builders.auth import AuthBuilder
from auto_test.demo_project.fixtures.conftest import *


@allure.feature("认证模块")
@allure.story("用户登录")
class TestAuthLogin:
    """用户登录接口测试"""

    @allure.title("正常登录")
    def test_login_success(self):
        """测试使用正确凭据登录"""
        auth_builder = AuthBuilder()
        token = auth_builder.login(
            username="testuser", password="482c811da5d5b4bc6d497ffa98491e38"
        )

        assert token is not None
        assert token.startswith("mock_token_")

    @allure.title("登录失败-用户名错误")
    def test_login_wrong_username(self):
        """测试使用错误用户名登录"""
        auth_builder = AuthBuilder()
        token = auth_builder.login(
            username="wronguser", password="482c811da5d5b4bc6d497ffa98491e38"
        )

        assert token is None

    @allure.title("登录失败-密码错误")
    def test_login_wrong_password(self):
        """测试使用错误密码登录"""
        auth_builder = AuthBuilder()
        token = auth_builder.login(username="testuser", password="wrongpassword")

        assert token is None

    @allure.title("登录失败-空用户名")
    def test_login_empty_username(self):
        """测试使用空用户名登录"""
        from auto_test.demo_project.api_manager import demo_project

        result = demo_project.auth.api_login(
            username="", password="482c811da5d5b4bc6d497ffa98491e38"
        )

        assert result.get("code") == 400
        assert "不能为空" in result.get("message", "")

    @allure.title("登录失败-空密码")
    def test_login_empty_password(self):
        """测试使用空密码登录"""
        from auto_test.demo_project.api_manager import demo_project

        result = demo_project.auth.api_login(username="testuser", password="")

        assert result.get("code") == 400
        assert "不能为空" in result.get("message", "")


@allure.feature("认证模块")
@allure.story("用户注册")
class TestAuthRegister:
    """用户注册接口测试"""

    @allure.title("正常注册")
    def test_register_success(self):
        """测试正常注册用户"""
        auth_builder = AuthBuilder()
        user = auth_builder.register()

        assert user is not None
        assert user.get("id") is not None
        assert user.get("username") is not None
        assert user.get("email") is not None

        # 清理
        from auto_test.demo_project.data_factory.builders.user import UserBuilder

        user_builder = UserBuilder()
        user_builder.delete(user_id=user.get("id"))

    @allure.title("注册-指定用户名")
    def test_register_with_username(self):
        """测试使用指定用户名注册"""
        import uuid

        auth_builder = AuthBuilder()
        username = f"test_{uuid.uuid4().hex[:8]}"
        user = auth_builder.register(username=username)

        assert user is not None
        assert user.get("username") == username

        # 清理
        from auto_test.demo_project.data_factory.builders.user import UserBuilder

        user_builder = UserBuilder()
        user_builder.delete(user_id=user.get("id"))

    @allure.title("注册失败-用户名已存在")
    def test_register_duplicate_username(self):
        """测试使用已存在用户名注册"""
        from auto_test.demo_project.api_manager import demo_project
        import uuid

        # 使用指定用户名注册
        username = f"dup_test_{uuid.uuid4().hex[:8]}"

        # 先注册一个用户
        result1 = demo_project.auth.api_register(
            username=username,
            email="test1@example.com",
            full_name="Test User 1",
            password="123456",
        )
        assert result1.get("code") == 200, f"第一次注册失败: {result1.get('message')}"
        user1 = result1.get("data")

        # 再用相同用户名注册
        result2 = demo_project.auth.api_register(
            username=username,
            email="test2@example.com",
            full_name="Test User 2",
            password="123456",
        )
        assert result2.get("code") == 400
        assert "已存在" in result2.get("message", "")

        # 清理
        from auto_test.demo_project.data_factory.builders.user import UserBuilder

        user_builder = UserBuilder()
        user_builder.delete(user_id=user1.get("id"))

    @allure.title("注册失败-空用户名")
    def test_register_empty_username(self):
        """测试使用空用户名注册"""
        from auto_test.demo_project.api_manager import demo_project

        result = demo_project.auth.api_register(
            username="",
            email="test@example.com",
            full_name="Test User",
            password="123456",
        )

        assert result.get("code") == 400
        assert "不能为空" in result.get("message", "")

    @allure.title("注册失败-空密码")
    def test_register_empty_password(self):
        """测试使用空密码注册"""
        from auto_test.demo_project.api_manager import demo_project

        result = demo_project.auth.api_register(
            username="testuser123",
            email="test@example.com",
            full_name="Test User",
            password="",
        )

        assert result.get("code") == 400
        assert "不能为空" in result.get("message", "")

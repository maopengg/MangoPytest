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
        auth_builder = AuthBuilder()
        token = auth_builder.login(
            username="", password="482c811da5d5b4bc6d497ffa98491e38"
        )

        assert token is None

    @allure.title("登录失败-空密码")
    def test_login_empty_password(self):
        """测试使用空密码登录"""
        auth_builder = AuthBuilder()
        token = auth_builder.login(username="testuser", password="")

        assert token is None


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
        user_builder.delete(user.get("id"))

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
        user_builder.delete(user.get("id"))

    @allure.title("注册失败-用户名已存在")
    def test_register_duplicate_username(self):
        """测试使用已存在用户名注册"""
        auth_builder = AuthBuilder()
        # 先注册一个用户
        user1 = auth_builder.register()
        assert user1 is not None

        # 再用相同用户名注册
        user2 = auth_builder.register(username=user1.get("username"))
        assert user2 is None

        # 清理
        from auto_test.demo_project.data_factory.builders.user import UserBuilder

        user_builder = UserBuilder()
        user_builder.delete(user1.get("id"))

    @allure.title("注册失败-空用户名")
    def test_register_empty_username(self):
        """测试使用空用户名注册"""
        auth_builder = AuthBuilder()
        user = auth_builder.register(username="")

        assert user is None

    @allure.title("注册失败-空密码")
    def test_register_empty_password(self):
        """测试使用空密码注册"""
        auth_builder = AuthBuilder()
        user = auth_builder.register(password="")

        assert user is None

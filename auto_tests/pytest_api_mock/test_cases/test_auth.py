# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 认证模块测试用例 - 新五层架构版本
# @Time   : 2026-04-06
# @Author : 毛鹏
"""
认证模块测试用例 - 使用新五层架构：
- L3: Pydantic Entity (UserEntityPydantic)
- L2: Pydantic Builder (AuthBuilderPydantic)
- L1: API Manager (pytest_api_mock.auth)
- L5: 测试用例层 (TestAuthLogin)

测试分层：
- 单接口测试（60%）
- 模块集成测试（30%）
- 端到端测试（10%）
"""

import allure
import pytest

from auto_tests.pytest_api_mock.api_manager import pytest_api_mock
from auto_tests.pytest_api_mock.data_factory.entities import UserEntityPydantic
from auto_tests.pytest_api_mock.data_factory.builders.auth.auth_builder_pydantic import (
    AuthBuilder,
)
from core.base.layering_base import UnitTest

@allure.epic('演示-pytest_api_mock')

@allure.feature("认证模块")
@allure.story("用户登录")
class TestAuthLogin(UnitTest):
    """用户登录接口测试 - 单接口测试（60%）"""

    @allure.title("正常登录 - 使用 L3 Entity 和 L2 Builder")
    def test_login_success_with_entity(self):
        """测试使用正确凭据登录 - 使用新五层架构"""
        # L3: 创建 Entity
        user = UserEntityPydantic.with_credentials(
            username="testuser", password="password123"
        )

        # L2: 使用 Builder 登录
        builder = AuthBuilder()
        token = builder.login(user)

        # 断言
        assert token is not None
        assert token.startswith("mock_token_")
        assert user.id is not None  # 验证响应字段已更新

    @allure.title("正常登录 - 使用 Fixture")
    def test_login_success_with_fixture(self, auth_builder_pydantic):
        """测试使用 fixture 登录"""
        user = UserEntityPydantic.with_credentials(
            username="testuser", password="password123"
        )
        token = auth_builder_pydantic.login(user)

        assert token is not None
        assert token.startswith("mock_token_")

    @allure.title("登录失败 - 用户名错误")
    def test_login_wrong_username(self):
        """测试使用错误用户名登录"""
        user = UserEntityPydantic.with_credentials(
            username="wronguser", password="password123"
        )
        builder = AuthBuilder()
        token = builder.login(user)

        assert token is None

    @allure.title("登录失败 - 密码错误")
    def test_login_wrong_password(self):
        """测试使用错误密码登录"""
        user = UserEntityPydantic.with_credentials(
            username="testuser", password="wrongpassword"
        )
        builder = AuthBuilder()
        token = builder.login(user)

        assert token is None

    @allure.title("登录失败 - 空用户名")
    def test_login_empty_username(self, api_client):
        """测试使用空用户名登录 - 直接调用 L1"""
        # 直接调用 L1 API（验证 L1 层）
        result = api_client.auth.api_login(username="", password="password123")

        self.assert_failure(result, expected_code=400)
        assert "不能为空" in result.get("message", "")

    @allure.title("登录失败 - 空密码")
    def test_login_empty_password(self, api_client):
        """测试使用空密码登录 - 直接调用 L1"""
        result = api_client.auth.api_login(username="testuser", password="")

        assert result.get("code") in [
            400,
            402,
        ], f"期望错误码 400 或 402，实际: {result.get('code')}"

    @allure.title("登录失败 - 用户不存在")
    def test_login_nonexistent_user(self):
        """测试登录不存在的用户"""
        user = UserEntityPydantic.with_credentials(
            username="nonexistent_user_12345", password="password123"
        )
        builder = AuthBuilder()
        token = builder.login(user)

        assert token is None


@allure.feature("认证模块")
@allure.story("用户注册")
class TestAuthRegister(UnitTest):
    """用户注册接口测试 - 单接口测试（60%）"""

    @allure.title("正常注册 - 使用 L3 Entity 和 L2 Builder")
    def test_register_success_with_entity(self, test_token):
        """测试正常注册 - 使用新五层架构"""
        # L3: 创建 Entity
        user = UserEntityPydantic.default()

        # L2: 使用 Builder 注册（传入 token 用于清理）
        builder = AuthBuilder(token=test_token)
        created = builder.register(user)

        # 断言
        assert created is not None
        assert created.id is not None  # 响应字段
        assert created.username == user.username

        # 清理
        builder.cleanup()

    @allure.title("正常注册 - 使用 Fixture")
    def test_register_success_with_fixture(self, auth_builder_pydantic):
        """测试使用 fixture 注册"""
        user = UserEntityPydantic.default()
        created = auth_builder_pydantic.register(user)

        assert created is not None
        assert created.id is not None

    @allure.title("注册失败 - 用户名已存在")
    def test_register_duplicate_username(self, api_client, test_token):
        """测试注册已存在的用户名 - 直接调用 L1"""
        import uuid

        unique_username = f"dup_test_{uuid.uuid4().hex[:8]}"

        # 先创建一个用户
        user1 = UserEntityPydantic.with_credentials(
            username=unique_username, password="password123"
        )
        builder = AuthBuilder(token=test_token)
        created = builder.register(user1)
        assert created is not None

        # 尝试使用相同用户名注册
        result = api_client.auth.api_register(
            username=unique_username,
            email="different@example.com",
            full_name="Different User",
            password="password123",
        )

        assert result.get("code") == 400
        builder.cleanup()

    @allure.title("注册失败 - 空用户名")
    def test_register_empty_username(self, api_client):
        """测试使用空用户名注册 - 直接调用 L1"""
        result = api_client.auth.api_register(
            username="",
            email="test@example.com",
            full_name="Test User",
            password="password123",
        )

        assert result.get("code") == 400


@allure.feature("认证模块")
@allure.story("Token 管理")
class TestTokenManagement(UnitTest):
    """Token 管理测试 - 单接口测试（60%）"""

    @allure.title("验证 Token 有效性")
    def test_token_validation(self, api_client):
        """测试验证 token 是否有效"""
        # 先登录获取 token
        user = UserEntityPydantic.with_credentials(
            username="testuser", password="password123"
        )
        builder = AuthBuilder()
        token = builder.login(user)

        assert token is not None

        # 使用 token 访问需要认证的接口
        api_client.auth.set_token(token)
        result = api_client.user.get_users()

        assert result.get("code") == 200

    @allure.title("使用无效 Token 访问")
    def test_invalid_token(self, api_client):
        """测试使用无效 token 访问"""
        from core.exceptions import ApiError

        # 创建一个无效的 token
        invalid_token = "invalid_token_12345"
        # 设置 token 到 API 客户端
        api_client.auth.set_token(invalid_token)

        # 应该抛出 401 异常
        with pytest.raises(ApiError) as exc_info:
            api_client.user.get_users()

        assert exc_info.value.code == 401

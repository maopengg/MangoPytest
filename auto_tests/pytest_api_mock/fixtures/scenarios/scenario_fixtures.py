# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 通用场景fixtures - 新架构
# @Time   : 2026-03-31
# @Author : 毛鹏
import pytest

from auto_tests.demo_project.data_factory.scenarios import (
    LoginScenario,
    RegisterAndLoginScenario,
)


@pytest.fixture
def login_scenario(authenticated_client) -> LoginScenario:
    """
    登录场景Fixture

    使用示例:
        def test_login(login_scenario):
            result = login_scenario.execute(username="test", password="123456")
            assert result.success
            assert "token" in result.data
    """
    scenario = LoginScenario(token=authenticated_client.token)
    yield scenario
    scenario.cleanup()


@pytest.fixture
def register_and_login_scenario(authenticated_client) -> RegisterAndLoginScenario:
    """
    注册并登录场景Fixture

    使用示例:
        def test_register_login(register_and_login_scenario):
            result = register_and_login_scenario.execute()
            assert result.success
            assert "token" in result.data
    """
    scenario = RegisterAndLoginScenario(token=authenticated_client.token)
    yield scenario
    scenario.cleanup()


@pytest.fixture
def logged_in_token(register_and_login_scenario) -> str:
    """
    已登录token Fixture
    自动注册新用户并登录，返回token

    使用示例:
        def test_with_token(logged_in_token):
            # 使用token进行后续操作
            headers = {"Authorization": f"Bearer {logged_in_token}"}
    """
    result = register_and_login_scenario.execute()
    assert result.success, f"登录失败: {result.message}"
    return result.data.get("token")

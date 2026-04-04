# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 认证模块 fixtures
# @Time   : 2026-03-31
# @Author : 毛鹏
from typing import Generator, Dict, Any

import pytest

from auto_test.demo_project.data_factory.builders.auth import AuthBuilder


@pytest.fixture(scope="session")
def auth_builder() -> AuthBuilder:
    """认证构造器 fixture"""
    return AuthBuilder()


@pytest.fixture(scope="function")
def test_token(auth_builder) -> Generator[str, None, None]:
    """
    测试用token fixture
    使用默认用户登录获取token
    """
    token = auth_builder.login()
    if not token:
        pytest.skip("无法获取测试token")

    yield token


@pytest.fixture(scope="function")
def registered_user(auth_builder) -> Generator[Dict[str, Any], None, None]:
    """
    已注册用户 fixture
    创建一个新用户并返回用户信息
    """
    user = auth_builder.register()
    if not user:
        pytest.skip("无法注册测试用户")

    yield user

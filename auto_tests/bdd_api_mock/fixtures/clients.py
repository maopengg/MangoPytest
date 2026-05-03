# -*- coding: utf-8 -*-
"""API 客户端 Fixtures"""
import hashlib
import pytest

from core.utils import log


@pytest.fixture(scope="session")
def mock_api_settings():
    """Mock API 测试配置"""
    from auto_tests.bdd_api_mock.config import get_config
    return get_config()


@pytest.fixture(scope="session")
def mock_api_client(mock_api_settings):
    """已认证的 API 客户端（session 级别）"""
    from auto_tests.bdd_api_mock.api_client import APIClient

    settings = mock_api_settings
    api = APIClient(base_url=settings.BASE_URL)

    password_md5 = hashlib.md5("password123".encode()).hexdigest()
    response = api.post("/auth/login", {"username": "testuser", "password": password_md5})

    if response.get("code") != 200:
        log.error(f">>> 认证失败: {response.get('message')}")
        raise RuntimeError(f"Failed to authenticate: {response.get('message')}")

    token = response["data"]["token"]
    api.set_token(token)
    yield api


@pytest.fixture
def api_client():
    """未认证的 API 客户端（用于登录测试）"""
    from auto_tests.bdd_api_mock.api_client import APIClient
    return APIClient()


@pytest.fixture(scope="session")
def db_session():
    """数据库会话（session 级别）"""
    from auto_tests.bdd_api_mock.config import get_config

    config = get_config()
    session = config.SessionLocal()
    try:
        yield session
    finally:
        session.close()

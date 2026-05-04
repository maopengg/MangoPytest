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
def api_client(mock_api_settings):
    """基础 API 客户端（session 级别）

    已认证，但不设置特定的 Content-Type
    """
    from core.api.client import APIClient

    settings = mock_api_settings
    api = APIClient(base_url=settings.BASE_URL)

    # 登录获取 token
    password_md5 = hashlib.md5("password123".encode()).hexdigest()
    response = api.request("POST", "/auth/login", json_data={
        "username": "testuser",
        "password": password_md5
    })

    if response.data.get("code") != 200:
        log.error(f">>> 认证失败: {response.data.get('message')}")
        raise RuntimeError(f"Failed to authenticate: {response.data.get('message')}")

    # 设置 token 到请求头
    token = response.data["data"]["token"]
    api.headers["Authorization"] = f"Bearer {token}"

    log.info(">>> API 客户端认证成功")

    yield api


@pytest.fixture
def json_client(api_client):
    """JSON 请求客户端

    Content-Type: application/json
    适用于：普通 API 请求，请求体为 JSON 格式
    """
    api_client.headers["Content-Type"] = "application/json"
    yield api_client


@pytest.fixture
def form_client(api_client):
    """表单请求客户端

    Content-Type: application/x-www-form-urlencoded
    适用于：表单提交
    """
    api_client.headers["Content-Type"] = "application/x-www-form-urlencoded"
    yield api_client


@pytest.fixture
def multipart_client(api_client):
    """文件上传客户端

    Content-Type: multipart/form-data（由 httpx 自动设置）
    适用于：文件上传
    """
    # 移除 Content-Type，让 httpx 自动设置 multipart boundary
    api_client.headers.pop("Content-Type", None)
    yield api_client


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

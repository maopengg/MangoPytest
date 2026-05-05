# -*- coding: utf-8 -*-
"""API 客户端 Fixtures"""
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

    登录认证由 BDD 步骤（如"管理员已登录"）完成
    使用方式:
        - 直接发送请求（默认 JSON 格式）
        - 通过 设置请求头 步骤自定义 Content-Type
    """
    from core.api.client import APIClient

    settings = mock_api_settings
    api = APIClient(base_url=settings.BASE_URL)

    # 设置全局默认请求头
    api.headers.update({
        "Content-Type": "application/json",
        "Accept": "application/json",
    })

    log.info(">>> API 客户端初始化完成")

    yield api


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

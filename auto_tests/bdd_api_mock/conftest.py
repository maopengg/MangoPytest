# -*- coding: utf-8 -*-
"""
pytest 全局配置 - BDD API Mock 测试

参考架构: bdd_api_ucai/conftest.py
"""

import pytest
import logging
import hashlib

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# ========== pytest-factoryboy 注册所有 Factories ==========
# 导入所有 spec 模块，@register 装饰器会自动注册 fixture
from auto_tests.bdd_api_mock.factories.specs.user import user_spec
from auto_tests.bdd_api_mock.factories.specs.auth import auth_spec
from auto_tests.bdd_api_mock.factories.specs.product import product_spec
from auto_tests.bdd_api_mock.factories.specs.order import order_spec
from auto_tests.bdd_api_mock.factories.specs.reimbursement import reimbursement_spec
from auto_tests.bdd_api_mock.factories.specs.approval import (
    dept_approval_spec,
    finance_approval_spec,
    ceo_approval_spec,
)
from auto_tests.bdd_api_mock.factories.specs.data import data_spec
from auto_tests.bdd_api_mock.factories.specs.file import file_spec
from auto_tests.bdd_api_mock.factories.specs.system import health_spec, api_log_spec

# ========== 导入步骤定义 ==========
# 使用 pytest_plugins 确保步骤定义在测试收集时加载
pytest_plugins = [
    # 通用 fixtures
    "auto_tests.bdd_api_mock.steps.common",
    # API 请求步骤
    "auto_tests.bdd_api_mock.steps.api.base",
    "auto_tests.bdd_api_mock.steps.api.entity",
    # 认证步骤
    "auto_tests.bdd_api_mock.steps.auth.login",
    # 数据准备步骤
    "auto_tests.bdd_api_mock.steps.data.factory",
    # 断言步骤
    "auto_tests.bdd_api_mock.steps.assertions.response",
    "auto_tests.bdd_api_mock.steps.assertions.data",
]


# ==================== 全局 Fixture ====================


@pytest.fixture(scope="session")
def mock_api_settings():
    """Mock API 测试配置"""
    from auto_tests.bdd_api_mock.config import settings

    return settings


@pytest.fixture(scope="session")
def mock_api_client(mock_api_settings):
    """已认证的 API 客户端

    类似 integration_api，自动登录获取 token
    """
    from auto_tests.bdd_api_mock.api_client import APIClient

    settings = mock_api_settings
    api = APIClient(base_url=settings.BASE_URL)

    logger.info(f">>> 正在认证: {settings.BASE_URL}")

    # 使用 testuser 登录
    password_md5 = hashlib.md5("password123".encode()).hexdigest()
    response = api.post(
        "/auth/login", {"username": "testuser", "password": password_md5}
    )

    if response.get("code") != 200:
        logger.error(f">>> 认证失败: {response.get('message')}")
        raise RuntimeError(f"Failed to authenticate: {response.get('message')}")

    token = response["data"]["token"]
    api.set_token(token)
    logger.info(">>> 认证成功")

    yield api


@pytest.fixture
def api_client():
    """未认证的 API 客户端（用于登录测试）"""
    from auto_tests.bdd_api_mock.api_client import APIClient

    return APIClient()


@pytest.fixture(scope="session")
def db_session():
    """数据库会话"""
    from auto_tests.bdd_api_mock.config import SessionLocal

    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def created_entity():
    """当前创建的实体

    用于在步骤间共享实体数据。返回一个字典，可以存储和更新实体。
    """
    return {}


# ========== 数据清理钩子 ==========


@pytest.fixture(scope="function", autouse=True)
def auto_cleanup_test_data(db_session):
    """自动清理自动化测试数据

    每个测试函数执行前清理 AUTO_ 开头的数据
    """
    from auto_tests.bdd_api_mock.hooks.cleanup_hooks import TestDataCleaner

    cleaner = TestDataCleaner(db_session)

    # 测试前清理
    logger.info(">>> [HOOK] 测试前清理 AUTO_ 测试数据...")
    try:
        cleaner.clear_all()
    except Exception as e:
        logger.warning(f">>> [HOOK] 数据清理失败: {e}")

    yield

    # 测试后清理（可选）
    # logger.info(">>> [HOOK] 测试后清理 AUTO_ 测试数据...")
    # cleaner.clear_all()


# ========== pytest 钩子 ==========


def pytest_configure(config):
    """pytest 配置钩子"""
    config.addinivalue_line("markers", "smoke: 冒烟测试")
    config.addinivalue_line("markers", "positive: 正向测试")
    config.addinivalue_line("markers", "negative: 负向测试")
    config.addinivalue_line("markers", "integration: 集成测试")

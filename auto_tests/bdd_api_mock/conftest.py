# -*- coding: utf-8 -*-
"""
pytest 全局配置 - BDD API Mock 测试

参考架构: bdd_api_ucai/conftest.py
"""

import pytest
import logging
import hashlib
import os
import tempfile

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


def _cleanup_test_data():
    """执行数据清理的内部函数"""
    try:
        from auto_tests.bdd_api_mock.config import SessionLocal
        from auto_tests.bdd_api_mock.hooks.cleanup_hooks import TestDataCleaner

        session = SessionLocal()
        try:
            cleaner = TestDataCleaner(session)
            cleaner.clear_all()
        finally:
            session.close()
    except Exception as e:
        logger.warning(f">>> [HOOK] 数据清理失败: {e}")


# ========== 多进程支持：会话级别清理 ==========

def pytest_configure(config):
    """pytest 配置钩子"""
    config.addinivalue_line("markers", "smoke: 冒烟测试")
    config.addinivalue_line("markers", "positive: 正向测试")
    config.addinivalue_line("markers", "negative: 负向测试")
    config.addinivalue_line("markers", "integration: 集成测试")


def _is_first_worker():
    """检查当前进程是否是第一个工作进程
    
    使用文件锁实现，只有第一个获取锁的进程返回 True
    """
    lock_file = os.path.join(tempfile.gettempdir(), 'bdd_api_mock_cleanup.lock')
    try:
        # 如果锁文件存在且被占用，说明已经有进程执行过清理
        if os.path.exists(lock_file):
            # 尝试读取锁文件中的进程ID
            try:
                with open(lock_file, 'r') as f:
                    content = f.read().strip()
                    if content:
                        return False  # 已经有进程执行过
            except:
                pass
        
        # 写入当前进程标识
        with open(lock_file, 'w') as f:
            f.write(str(os.getpid()))
        return True
    except Exception as e:
        logger.warning(f">>> 检查锁文件失败: {e}")
        return False


def pytest_sessionstart(session):
    """测试会话开始时执行
    
    在多进程模式下，只有第一个工作进程执行清理
    """
    worker_id = os.environ.get('PYTEST_XDIST_WORKER')
    
    if worker_id:
        # 工作进程：只有第一个工作进程执行清理
        if worker_id == 'gw0':  # xdist 的第一个工作进程
            logger.info(f">>> [Worker {worker_id}] 第一个工作进程，执行数据清理...")
            _cleanup_test_data()
        else:
            logger.info(f">>> [Worker {worker_id}] 非首个工作进程，跳过清理")
    else:
        # 主进程（非多进程模式）
        logger.info(">>> [Main] 测试会话开始，执行数据清理...")
        _cleanup_test_data()


def pytest_sessionfinish(session, exitstatus):
    """测试会话结束时执行
    
    清理锁文件
    """
    worker_id = os.environ.get('PYTEST_XDIST_WORKER')
    
    # 只有主进程或第一个工作进程清理锁文件
    if not worker_id or worker_id == 'gw0':
        lock_file = os.path.join(tempfile.gettempdir(), 'bdd_api_mock_cleanup.lock')
        try:
            if os.path.exists(lock_file):
                os.remove(lock_file)
                logger.info(">>> 清理锁文件")
        except Exception as e:
            logger.warning(f">>> 清理锁文件失败: {e}")

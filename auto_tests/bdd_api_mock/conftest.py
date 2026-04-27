# -*- coding: utf-8 -*-
"""
pytest 全局配置 - BDD API Mock 测试

参考架构: bdd_api_ucai/conftest.py
"""
import traceback

import pytest
import hashlib
import os
import tempfile
import time

from core.utils import log

# ========== pytest-factoryboy 注册所有 Factories ==========
# 导入所有 spec 模块，@register 装饰器会自动注册 fixture
# 从 data_factory 导入（数据工厂统一入口）
from auto_tests.bdd_api_mock.data_factory.specs.user import user_spec
from auto_tests.bdd_api_mock.data_factory.specs.auth import auth_spec
from auto_tests.bdd_api_mock.data_factory.specs.product import product_spec
from auto_tests.bdd_api_mock.data_factory.specs.order import order_spec
from auto_tests.bdd_api_mock.data_factory.specs.reimbursement import reimbursement_spec
from auto_tests.bdd_api_mock.data_factory.specs.approval import (
    dept_approval_spec,
    finance_approval_spec,
    ceo_approval_spec,
)
from auto_tests.bdd_api_mock.data_factory.specs.data import data_spec
from auto_tests.bdd_api_mock.data_factory.specs.file import file_spec
from auto_tests.bdd_api_mock.data_factory.specs.system import health_spec, api_log_spec

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
    from auto_tests.bdd_api_mock.config import get_config

    return get_config()


@pytest.fixture(scope="session")
def mock_api_client(mock_api_settings):
    """已认证的 API 客户端

    类似 integration_api，自动登录获取 token
    """
    from auto_tests.bdd_api_mock.api_client import APIClient

    settings = mock_api_settings
    api = APIClient(base_url=settings.BASE_URL)

    log.info(f">>> 正在认证: {settings.BASE_URL}")

    # 使用 testuser 登录
    password_md5 = hashlib.md5("password123".encode()).hexdigest()
    response = api.post(
        "/auth/login", {"username": "testuser", "password": password_md5}
    )

    if response.get("code") != 200:
        log.error(f">>> 认证失败: {response.get('message')}")
        raise RuntimeError(f"Failed to authenticate: {response.get('message')}")

    token = response["data"]["token"]
    api.set_token(token)
    log.info(">>> 认证成功")

    yield api


@pytest.fixture
def api_client():
    """未认证的 API 客户端（用于登录测试）"""
    from auto_tests.bdd_api_mock.api_client import APIClient

    return APIClient()


@pytest.fixture(scope="session")
def db_session():
    """数据库会话"""
    from auto_tests.bdd_api_mock.config import get_config

    config = get_config()
    session = config.SessionLocal()
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
        from auto_tests.bdd_api_mock.config import get_config
        from auto_tests.bdd_api_mock.hooks.cleanup_hooks import TestDataCleaner

        config = get_config()
        session = config.SessionLocal()
        try:
            cleaner = TestDataCleaner(session)
            cleaner.clear_all()
        finally:
            session.close()
    except Exception as e:
        traceback.print_exc()
        log.warning(f">>> [HOOK] 数据清理失败: {e}")


# ========== 多进程支持：会话级别清理 ==========


def pytest_configure(config):
    """pytest 配置钩子"""
    config.addinivalue_line("markers", "smoke: 冒烟测试")
    config.addinivalue_line("markers", "positive: 正向测试")
    config.addinivalue_line("markers", "negative: 负向测试")
    config.addinivalue_line("markers", "integration: 集成测试")


def _try_acquire_cleanup_lock():
    """
    尝试获取清理锁
    
    使用文件锁机制确保只有一个进程执行清理
    返回 True 表示获取锁成功，False 表示锁已被其他进程持有
    """
    lock_file = os.path.join(tempfile.gettempdir(), 'bdd_api_mock_cleanup.lock')
    pid_file = os.path.join(tempfile.gettempdir(), 'bdd_api_mock_cleanup.pid')
    
    try:
        # 检查是否有其他进程正在执行清理（5秒内）
        if os.path.exists(pid_file):
            try:
                with open(pid_file, 'r') as f:
                    content = f.read().strip()
                    if content:
                        pid, timestamp = content.split(',')
                        # 如果5秒内已经有进程执行过，跳过
                        if time.time() - float(timestamp) < 5:
                            return False
            except:
                pass
        
        # 写入当前进程信息
        with open(pid_file, 'w') as f:
            f.write(f"{os.getpid()},{time.time()}")
        
        return True
    except Exception as e:
        log.warning(f">>> 获取清理锁失败: {e}")
        return False


def pytest_sessionstart(session):
    """测试会话开始时执行
    
    使用文件锁确保只有一个进程执行清理
    """
    worker_id = os.environ.get('PYTEST_XDIST_WORKER')
    
    # 尝试获取锁
    if _try_acquire_cleanup_lock():
        if worker_id:
            log.info(f">>> [Worker {worker_id}] 获取清理锁，执行数据清理...")
        else:
            log.info(">>> [Main] 获取清理锁，执行数据清理...")
        _cleanup_test_data()
    else:
        if worker_id:
            log.info(f">>> [Worker {worker_id}] 清理锁已被占用，跳过清理")
        else:
            log.info(">>> [Main] 清理锁已被占用，跳过清理")


def pytest_sessionfinish(session, exitstatus):
    """测试会话结束时执行
    
    清理锁文件
    """
    # 只有获取锁的进程清理文件
    pid_file = os.path.join(tempfile.gettempdir(), 'bdd_api_mock_cleanup.pid')
    try:
        if os.path.exists(pid_file):
            with open(pid_file, 'r') as f:
                content = f.read().strip()
                if content:
                    pid, _ = content.split(',')
                    if int(pid) == os.getpid():
                        os.remove(pid_file)
                        log.info(">>> 清理锁文件")
    except Exception as e:
        log.warning(f">>> 清理锁文件失败: {e}")

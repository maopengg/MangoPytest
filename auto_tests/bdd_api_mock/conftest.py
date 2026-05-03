# -*- coding: utf-8 -*-
"""
pytest 全局配置 - BDD API Mock 测试

参照架构: qfei_contract_api/conftest.py
"""
import os
import tempfile
import time
import traceback

import pytest

from core.utils import log

# ========== pytest-factoryboy 注册所有 Factories ==========
from auto_tests.bdd_api_mock.data_factory.specs.user import user_spec          # noqa: F401
from auto_tests.bdd_api_mock.data_factory.specs.auth import auth_spec          # noqa: F401
from auto_tests.bdd_api_mock.data_factory.specs.product import product_spec    # noqa: F401
from auto_tests.bdd_api_mock.data_factory.specs.order import order_spec        # noqa: F401
from auto_tests.bdd_api_mock.data_factory.specs.reimbursement import reimbursement_spec  # noqa: F401
from auto_tests.bdd_api_mock.data_factory.specs.approval import (
    dept_approval_spec,        # noqa: F401
    finance_approval_spec,     # noqa: F401
    ceo_approval_spec,         # noqa: F401
)
from auto_tests.bdd_api_mock.data_factory.specs.data import data_spec          # noqa: F401
from auto_tests.bdd_api_mock.data_factory.specs.file import file_spec          # noqa: F401
from auto_tests.bdd_api_mock.data_factory.specs.system import health_spec, api_log_spec  # noqa: F401

# ========== 自动发现步骤定义和 fixture 模块 ==========

from pathlib import Path

CONFTEST_DIR = Path(__file__).parent

# 核心断言步骤
pytest_plugins = [
    "core.api.bdd_steps",
]


def _discover_modules(rel_dir: str, pkg_name: str):
    """自动发现指定目录下的所有 Python 模块（不含 __init__）"""
    base = CONFTEST_DIR / rel_dir
    if not base.is_dir():
        return
    for pyfile in sorted(base.rglob("*.py")):
        if pyfile.name == "__init__.py":
            continue
        rel = pyfile.relative_to(base).with_suffix("")
        mod = f"{pkg_name}.{rel.as_posix().replace('/', '.')}"
        pytest_plugins.append(mod)


# 自动发现步骤定义模块
_discover_modules("steps", "auto_tests.bdd_api_mock.steps")

# 自动发现 fixture 模块
_discover_modules("fixtures", "auto_tests.bdd_api_mock.fixtures")

del Path, CONFTEST_DIR, _discover_modules


# ========== 日志配置 ==========

def pytest_configure(config):
    """pytest 配置钩子"""
    import logging
    for name in ["core", "auto_tests", "mangotools"]:
        logging.getLogger(name).propagate = False

    config.addinivalue_line("markers", "smoke: 冒烟测试")
    config.addinivalue_line("markers", "positive: 正向测试")
    config.addinivalue_line("markers", "negative: 负向测试")
    config.addinivalue_line("markers", "integration: 集成测试")


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


def _try_acquire_cleanup_lock():
    """尝试获取清理锁"""
    pid_file = os.path.join(tempfile.gettempdir(), 'bdd_api_mock_cleanup.pid')

    try:
        if os.path.exists(pid_file):
            try:
                with open(pid_file, 'r') as f:
                    content = f.read().strip()
                    if content:
                        pid, timestamp = content.split(',')
                        if time.time() - float(timestamp) < 5:
                            return False
            except Exception:
                pass

        with open(pid_file, 'w') as f:
            f.write(f"{os.getpid()},{time.time()}")

        return True
    except Exception as e:
        log.warning(f">>> 获取清理锁失败: {e}")
        return False


def pytest_sessionstart(session):
    """测试会话开始时清理数据"""
    worker_id = os.environ.get('PYTEST_XDIST_WORKER')

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
    """测试会话结束时清理锁文件"""
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

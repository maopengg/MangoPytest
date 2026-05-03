# -*- coding: utf-8 -*-
"""bdd_ui_mock Pytest 配置 — 自动发现步骤和 fixture 模块"""
import os
import tempfile
import time
import traceback

import pytest

from core.utils import log

# ========== 自动发现步骤和 fixture 模块 ==========

# 核心步骤
pytest_plugins = [
    "core.api.bdd_steps",
]

from pathlib import Path

CONFTEST_DIR = Path(__file__).parent


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


_discover_modules("steps", "auto_tests.bdd_ui_mock.steps")
_discover_modules("fixtures", "auto_tests.bdd_ui_mock.fixtures")

del Path, CONFTEST_DIR, _discover_modules


# ========== 数据库会话 ==========

@pytest.fixture(scope="session")
def db_session():
    """数据库会话（session 级别）"""
    from auto_tests.bdd_ui_mock.config import get_config

    config = get_config()
    if not config.SessionLocal:
        yield None
        return
    session = config.SessionLocal()
    try:
        yield session
    finally:
        session.close()


# ========== 日志配置 ==========

def pytest_configure(config):
    import logging
    for name in ["core", "auto_tests", "mangotools"]:
        logging.getLogger(name).propagate = False

    config.addinivalue_line("markers", "smoke: 冒烟测试")
    config.addinivalue_line("markers", "ui: UI 自动化测试")
    config.addinivalue_line("markers", "positive: 正向测试场景")
    config.addinivalue_line("markers", "negative: 负向测试场景")


# ========== 数据清理钩子 ==========

def _cleanup_test_data():
    """执行数据清理的内部函数"""
    try:
        from auto_tests.bdd_ui_mock.config import get_config
        from auto_tests.bdd_ui_mock.hooks.cleanup_hooks import TestDataCleaner

        config = get_config()
        if not config.SessionLocal:
            return
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
    pid_file = os.path.join(tempfile.gettempdir(), 'bdd_ui_mock_cleanup.pid')
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
    if _try_acquire_cleanup_lock():
        _cleanup_test_data()


def pytest_sessionfinish(session, exitstatus):
    """测试会话结束时清理锁文件"""
    pid_file = os.path.join(tempfile.gettempdir(), 'bdd_ui_mock_cleanup.pid')
    try:
        if os.path.exists(pid_file):
            with open(pid_file, 'r') as f:
                content = f.read().strip()
                if content:
                    pid, _ = content.split(',')
                    if int(pid) == os.getpid():
                        os.remove(pid_file)
    except Exception as e:
        log.warning(f">>> 清理锁文件失败: {e}")

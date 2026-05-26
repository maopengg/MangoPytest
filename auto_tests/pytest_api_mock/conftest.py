# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: pytest配置文件 - 新架构
# @Time   : 2026-03-31
# @Author : 毛鹏

from auto_tests.pytest_api_mock.fixtures.conftest import *
from core.reporting import *


def pytest_sessionfinish(session, exitstatus):
    """测试会话结束后兜底清理自动化测试数据。"""
    from auto_tests.pytest_api_mock.hooks.cleanup_hooks import cleanup_auto_test_data

    cleanup_auto_test_data()

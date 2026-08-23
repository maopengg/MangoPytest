# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: Web 驱动 Fixtures
# @Time   : 2026-04-25
# @Author : 毛鹏
"""
Web 驱动 Fixtures 模块

提供 Web 驱动相关的 fixtures：
- web_runtime: Web 驱动对象（session 级别）
"""

import pytest
from mangoautomation.uidrives import WebDriverFactory

from core.enums.ui_enum import BrowserTypeEnum
from core.utils import log
from auto_tests.ui.simple_ui.config import settings


@pytest.fixture(scope="session")
def web_runtime():
    """
    Web 驱动对象 fixture

    整个测试会话期间共享一个驱动对象

    使用示例：
        def test_example(web_runtime):
            context, page = web_runtime.new_context_page()
            page.goto("https://example.com")
    """
    runtime = WebDriverFactory.create_sync_runtime(
        web_type=BrowserTypeEnum.CHROMIUM.value,
        web_max=not settings.HEADLESS,
        web_headers=settings.HEADLESS,
        set_default_timeout=settings.IMPLICIT_WAIT,
        log=log,
    )
    yield runtime
    # 会话结束时清理
    try:
        runtime.close()
    except Exception:
        pass

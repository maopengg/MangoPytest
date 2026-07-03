# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: Web 驱动 Fixtures
# @Time   : 2026-04-25
# @Author : 毛鹏
"""
Web 驱动 Fixtures 模块

提供 Web 驱动相关的 fixtures：
- driver_object: Web 驱动对象（session 级别）
"""

import pytest
from mangoautomation.uidrive import DriverObject

from core.enums.ui_enum import BrowserTypeEnum
from core.utils import log


@pytest.fixture(scope="session")
def driver_object():
    """
    Web 驱动对象 fixture

    整个测试会话期间共享一个驱动对象

    使用示例：
        def test_example(driver_object):
            context, page = driver_object.web.new_web_page()
            page.goto("https://example.com")
    """
    driver = DriverObject(log)
    driver.set_web(web_type=BrowserTypeEnum.CHROMIUM.value, web_max=True)
    yield driver
    # 会话结束时清理
    try:
        driver.web.close()
    except Exception:
        pass

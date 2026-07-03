# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: UI Mock Fixtures 注册中心
# @Time   : 2026-04-25
# @Author : 毛鹏
"""
UI Mock 项目的 Fixtures 注册中心

此文件集中注册所有 fixtures，便于管理和使用。
在测试文件中只需导入此模块即可使用所有 fixtures。

使用示例：
    # test_example.py
    from auto_tests.ui_mock.fixtures.conftest import *

    def test_with_driver(driver_object):
        context, page = driver_object.web.new_web_page()
        page.goto("https://example.com")

    def test_with_base_data(base_data):
        from auto_tests.ui_mock.abstract.home_page import HomePage
        home_page = HomePage(base_data, test_data)
        home_page.goto()
"""

# ========== 基础设施 fixtures ==========
from auto_tests.ui_mock.fixtures.infra.client import (
    driver_object,
)
from auto_tests.ui_mock.fixtures.infra.base_data import (
    base_data,
)

__all__ = [
    # 基础设施
    "driver_object",
    "base_data",
]

# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: UI Mock 测试用例 Fixtures
# @Time   : 2026-04-25
# @Author : 毛鹏
"""
UI Mock 测试用例目录的 Pytest Fixtures

此文件确保从 test_cases 目录运行测试时也能找到 fixtures
所有的 fixtures 实际定义在父目录的 fixtures/ 模块中
"""

from auto_tests.ui.simple_ui.fixtures.conftest import *


# 旧页面对象用例依赖已废弃的中文元素/远端元素源，功能已由
# test_excel_ui_cases.py 的 493 条 Excel 用例完整覆盖，不再参与正式收集。
collect_ignore = [
    "test_alert.py",
    "test_batch.py",
    "test_click.py",
    "test_flash.py",
    "test_iframe.py",
    "test_input.py",
    "test_keyboard.py",
    "test_mouse.py",
    "test_navigation.py",
    "test_scroll.py",
    "test_upload.py",
]

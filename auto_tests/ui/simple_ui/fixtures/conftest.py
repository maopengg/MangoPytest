# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: UI Mock Fixtures 注册中心
# @Time   : 2026-04-25
# @Author : 毛鹏
"""
UI Mock 项目的 Fixtures 注册中心

此文件集中注册所有 fixtures，便于管理和使用。
在测试文件中只需导入此模块即可使用所有 fixtures。

正式 Case 统一位于 ``test_cases/capabilities/``，通过 ``ExcelCasePage``
执行本地 Excel 声明的操作、交互和元素定位能力。
"""

# ========== 基础设施 fixtures ==========
from auto_tests.ui.simple_ui.fixtures.infra.client import (
    web_runtime,
)
from auto_tests.ui.simple_ui.fixtures.infra.base_data import (
    base_data,
)

__all__ = [
    # 基础设施
    "web_runtime",
    "base_data",
]

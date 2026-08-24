# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: UI Mock Fixtures 注册中心
# @Time   : 2026-04-25
# @Author : 毛鹏
"""
UI Mock 项目的 Fixtures 注册中心

此文件集中注册所有 fixtures，便于管理和使用。
在测试文件中只需导入此模块即可使用所有 fixtures。

项目用例直接声明所需 fixture；Page Object 与 Flow 由 fixture 完成装配。
"""

# ========== 基础设施 fixtures ==========
from auto_tests.ui.pytest_ui.fixtures.infra.client import (
    web_runtime,
)
from auto_tests.ui.pytest_ui.fixtures.infra.base_data import (
    base_data,
)
from auto_tests.ui.pytest_ui.fixtures.business import claim_flow, order_flow, review_flow
from auto_tests.ui.pytest_ui.fixtures.data_factory import ui_data_factory, ui_repositories

__all__ = [
    # 基础设施
    "web_runtime",
    "base_data",
    "ui_data_factory",
    "ui_repositories",
    "order_flow",
    "claim_flow",
    "review_flow",
]

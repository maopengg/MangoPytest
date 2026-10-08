# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: UI Mock 项目 Pytest 配置
# @Time   : 2026-04-25
# @Author : 毛鹏
"""
UI Mock 项目的 Pytest 配置文件

从 fixtures 模块导入所有 fixtures
"""

import pytest

from auto_tests.common.mango_mock.ui_cases import is_ai_heal_case
from auto_tests.ui.simple_ui.fixtures.conftest import *  # noqa: F401,F403


def pytest_collection_modifyitems(items):
    """把以元素自愈靶场为目标的用例标记为 ``ai_heal``。

    AI 元素定位默认关闭，定向验证时用 ``-m ai_heal`` 只跑这一小撮用例，
    避免为验证 AI 而全量开启（库侧没有"只观察不执行"的模式）。
    """

    for item in items:
        callspec = getattr(item, "callspec", None)
        if not callspec:
            continue
        # 元素用例参数名为 element_case，操作用例为 operation_case。
        for key in ("element_case", "operation_case"):
            case = callspec.params.get(key)
            if case is not None and is_ai_heal_case(case):
                item.add_marker(pytest.mark.ai_heal)
                break

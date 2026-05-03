# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: bdd_ui_mock Pytest 配置
# @Time   : 2026-05-03
# @Author : 毛鹏
"""bdd_ui_mock Pytest 配置 — 通过 pytest_plugins 注册步骤定义"""
import pytest

pytest_plugins = [
    "auto_tests.bdd_ui_mock.steps.common",
    "auto_tests.bdd_ui_mock.steps.home.home_steps",
    "auto_tests.bdd_ui_mock.steps.alert_steps",
    "auto_tests.bdd_ui_mock.steps.batch_steps",
    "auto_tests.bdd_ui_mock.steps.click_steps",
    "auto_tests.bdd_ui_mock.steps.flash_steps",
    "auto_tests.bdd_ui_mock.steps.iframe_steps",
    "auto_tests.bdd_ui_mock.steps.input_steps",
    "auto_tests.bdd_ui_mock.steps.keyboard_steps",
    "auto_tests.bdd_ui_mock.steps.mouse_steps",
    "auto_tests.bdd_ui_mock.steps.navigation_steps",
    "auto_tests.bdd_ui_mock.steps.scroll_steps",
    "auto_tests.bdd_ui_mock.steps.upload_steps",
]


@pytest.fixture(scope="session")
def ui_config():
    from auto_tests.bdd_ui_mock.config import settings
    return settings

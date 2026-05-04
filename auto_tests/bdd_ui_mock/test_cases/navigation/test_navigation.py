# -*- coding: utf-8 -*-
"""页面导航 BDD 测试绑定"""
import allure
from pytest_bdd import scenarios

pytestmark = [
    allure.epic("BDD UI Mock 测试"),
    allure.feature("页面导航"),
    allure.story("页面导航验证"),
]

scenarios("test_navigation.feature")

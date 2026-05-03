# -*- coding: utf-8 -*-
"""页面滚动 BDD 测试绑定"""
import allure
from pytest_bdd import scenarios

pytestmark = [
    allure.epic("BDD UI Mock 测试"),
    allure.feature("页面滚动"),
    allure.story("页面滚动验证"),
]

scenarios("scroll.feature")

# -*- coding: utf-8 -*-
"""输入框 BDD 测试绑定"""
import allure
from pytest_bdd import scenarios

pytestmark = [
    allure.epic("BDD UI Mock 测试"),
    allure.feature("输入框"),
    allure.story("输入操作验证"),
]

scenarios("test_input.feature")

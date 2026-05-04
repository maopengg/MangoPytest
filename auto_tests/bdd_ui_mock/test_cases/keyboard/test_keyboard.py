# -*- coding: utf-8 -*-
"""键盘操作 BDD 测试绑定"""
import allure
from pytest_bdd import scenarios

pytestmark = [
    allure.epic("BDD UI Mock 测试"),
    allure.feature("键盘操作"),
    allure.story("键盘操作验证"),
]

scenarios("test_keyboard.feature")

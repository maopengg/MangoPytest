# -*- coding: utf-8 -*-
"""鼠标操作 BDD 测试绑定"""
import allure
from pytest_bdd import scenarios

pytestmark = [
    allure.epic("BDD UI Mock 测试"),
    allure.feature("鼠标操作"),
    allure.story("鼠标操作验证"),
]

scenarios("mouse.feature")

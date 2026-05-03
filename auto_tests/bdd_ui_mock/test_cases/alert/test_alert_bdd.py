# -*- coding: utf-8 -*-
"""浏览器弹窗 BDD 测试绑定"""
import allure
from pytest_bdd import scenarios

pytestmark = [
    allure.epic("BDD UI Mock 测试"),
    allure.feature("浏览器弹窗"),
    allure.story("弹窗验证"),
]

scenarios("alert.feature")

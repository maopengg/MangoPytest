# -*- coding: utf-8 -*-
"""元素点击 BDD 测试绑定"""
import allure
from pytest_bdd import scenarios

pytestmark = [
    allure.epic("BDD UI Mock 测试"),
    allure.feature("元素点击"),
    allure.story("点击操作验证"),
]

scenarios("click.feature")

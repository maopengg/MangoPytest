# -*- coding: utf-8 -*-
"""闪现元素 BDD 测试绑定"""
import allure
from pytest_bdd import scenarios

pytestmark = [
    allure.epic("BDD UI Mock 测试"),
    allure.feature("闪现元素"),
    allure.story("闪现元素验证"),
]

scenarios("flash.feature")

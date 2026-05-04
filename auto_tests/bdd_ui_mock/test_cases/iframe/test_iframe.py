# -*- coding: utf-8 -*-
"""iframe BDD 测试绑定"""
import allure
from pytest_bdd import scenarios

pytestmark = [
    allure.epic("BDD UI Mock 测试"),
    allure.feature("iframe"),
    allure.story("iframe 操作验证"),
]

scenarios("test_iframe.feature")

# -*- coding: utf-8 -*-
"""首页 BDD 测试绑定"""
import allure
from pytest_bdd import scenarios

pytestmark = [
    allure.epic("BDD UI Mock 测试"),
    allure.feature("Mock 首页"),
    allure.story("首页访问"),
]

scenarios("home.feature")

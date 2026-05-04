# -*- coding: utf-8 -*-
"""批量操作 BDD 测试绑定"""
import allure
from pytest_bdd import scenarios

pytestmark = [
    allure.epic("BDD UI Mock 测试"),
    allure.feature("批量操作"),
    allure.story("批量操作验证"),
]

scenarios("test_batch.feature")

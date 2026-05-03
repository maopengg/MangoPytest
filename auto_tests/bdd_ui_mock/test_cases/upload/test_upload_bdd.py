# -*- coding: utf-8 -*-
"""文件上传 BDD 测试绑定"""
import allure
from pytest_bdd import scenarios

pytestmark = [
    allure.epic("BDD UI Mock 测试"),
    allure.feature("文件上传"),
    allure.story("文件上传验证"),
]

scenarios("upload.feature")

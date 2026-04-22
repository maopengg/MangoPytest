# -*- coding: utf-8 -*-
"""
调试导入测试
"""

from pytest_bdd import scenarios, given, when, then, parsers

# 导入步骤定义
print("Importing data_steps...")
from auto_tests.bdd_api_mock.steps.data_steps import *
print("data_steps imported")

print("Importing api_steps...")
from auto_tests.bdd_api_mock.steps.api_steps import *
print("api_steps imported")

print("Importing assertion_steps...")
from auto_tests.bdd_api_mock.steps.assertion_steps import *
print("assertion_steps imported")

# 检查 api_get_step 是否存在
try:
    print(f"api_get_step: {api_get_step}")
except NameError:
    print("api_get_step not found!")

# 加载 feature 文件
scenarios("user.feature")


@given('管理员已登录')
def admin_logged_in():
    """管理员已登录步骤"""
    print("管理员已登录")

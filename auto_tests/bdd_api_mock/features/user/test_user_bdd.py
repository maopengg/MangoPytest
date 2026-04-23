# -*- coding: utf-8 -*-
"""
用户管理 BDD 测试
"""

import allure
from pytest_bdd import scenarios

# Allure 分组配置
allure.feature("用户管理")
allure.story("用户CRUD操作")

# 加载 feature 文件
scenarios("user.feature")

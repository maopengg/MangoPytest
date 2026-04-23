# -*- coding: utf-8 -*-
"""
用户认证 BDD 测试
"""

import allure
from pytest_bdd import scenarios

# Allure 分组配置
allure.feature("认证模块")
allure.story("用户登录")

# 加载 feature 文件
scenarios("auth.feature")

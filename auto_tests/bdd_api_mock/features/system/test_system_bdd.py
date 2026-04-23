# -*- coding: utf-8 -*-
"""
系统管理 BDD 测试
"""

import allure
from pytest_bdd import scenarios

# Allure 分组配置
allure.feature("系统模块")
allure.story("系统状态监控")

# 加载 feature 文件
scenarios("system.feature")

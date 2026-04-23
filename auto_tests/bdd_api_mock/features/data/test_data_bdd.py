# -*- coding: utf-8 -*-
"""
数据提交管理 BDD 测试
"""

import allure
from pytest_bdd import scenarios

# Allure 分组配置
allure.feature("数据模块")
allure.story("数据提交操作")

# 加载 feature 文件
scenarios("data.feature")

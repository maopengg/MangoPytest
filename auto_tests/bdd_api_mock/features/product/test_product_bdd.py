# -*- coding: utf-8 -*-
"""
产品管理 BDD 测试
"""

import allure
from pytest_bdd import scenarios

# Allure 分组配置
allure.feature("产品模块")
allure.story("产品CRUD操作")

# 加载 feature 文件
scenarios("product.feature")

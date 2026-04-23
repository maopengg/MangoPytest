# -*- coding: utf-8 -*-
"""
订单管理 BDD 测试
"""

import allure
from pytest_bdd import scenarios

# Allure 分组配置
allure.feature("订单模块")
allure.story("订单CRUD操作")

# 加载 feature 文件
scenarios("order.feature")

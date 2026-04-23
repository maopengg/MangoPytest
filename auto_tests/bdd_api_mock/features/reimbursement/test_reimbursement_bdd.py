# -*- coding: utf-8 -*-
"""
报销申请管理 BDD 测试
"""

import allure
from pytest_bdd import scenarios

# Allure 分组配置
allure.feature("报销模块")
allure.story("报销申请CRUD操作")

# 加载 feature 文件
scenarios("reimbursement.feature")

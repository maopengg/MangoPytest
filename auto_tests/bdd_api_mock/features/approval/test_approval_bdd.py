# -*- coding: utf-8 -*-
"""
审批流程管理 BDD 测试
"""

import allure
from pytest_bdd import scenarios

# Allure 分组配置
allure.feature("审批模块")
allure.story("审批流程操作")

# 加载 feature 文件
scenarios("approval.feature")

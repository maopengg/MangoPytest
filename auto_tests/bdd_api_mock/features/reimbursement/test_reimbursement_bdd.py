# -*- coding: utf-8 -*-
"""
报销申请管理 BDD 测试
"""

from pytest_bdd import scenarios

# 加载 feature 文件
scenarios("reimbursement.feature")

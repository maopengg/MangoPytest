# -*- coding: utf-8 -*-
"""
系统管理 BDD 测试
"""

from pytest_bdd import scenarios

# 加载 feature 文件
scenarios("system.feature")

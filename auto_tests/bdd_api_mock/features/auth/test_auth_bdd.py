# -*- coding: utf-8 -*-
"""
用户认证 BDD 测试
"""

from pytest_bdd import scenarios

# 加载 feature 文件
scenarios("auth.feature")

# -*- coding: utf-8 -*-
"""
系统管理 BDD 测试
"""

import pytest
import allure
from pytest_bdd import scenarios

# Allure 分组配置 - 三级结构：Epic > Feature > Story
pytestmark = [
    allure.epic("BDD API Mock 测试"),
    allure.feature("系统管理"),
    allure.story("系统状态监控"),
]

# 加载 feature 文件
scenarios("system.feature")

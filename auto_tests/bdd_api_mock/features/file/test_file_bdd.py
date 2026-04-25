# -*- coding: utf-8 -*-
"""
文件管理 BDD 测试
"""

import pytest
import allure
from pytest_bdd import scenarios

# Allure 分组配置 - 三级结构：Epic > Feature > Story
pytestmark = [
    allure.epic("BDD API Mock 测试"),
    allure.feature("文件管理"),
    allure.story("文件上传操作"),
]

# 加载 feature 文件
scenarios("file.feature")

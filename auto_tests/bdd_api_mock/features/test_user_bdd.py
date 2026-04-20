# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 用户管理模块 BDD 测试
# @Time   : 2026-04-17
# @Author : 毛鹏
"""
用户管理模块 BDD 测试

此文件使用 pytest-bdd 运行 user.feature 中的场景
"""

# 导入 conftest 中的步骤定义
import auto_tests.bdd_api_mock.features.conftest

from pytest_bdd import scenarios

# 加载 feature 文件
scenarios("user.feature")

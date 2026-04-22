# -*- coding: utf-8 -*-
"""
用户管理 BDD 测试
"""

import json
from pytest_bdd import scenarios, given, when, then, parsers

# 导入步骤定义（必须在 scenarios 之前导入）
from auto_tests.bdd_api_mock.steps.data_steps import *
from auto_tests.bdd_api_mock.steps.assertion_steps import *
from auto_tests.bdd_api_mock.steps.api_steps import *
from auto_tests.bdd_api_mock.steps.auth_steps import *

# 加载 feature 文件
scenarios("user.feature")

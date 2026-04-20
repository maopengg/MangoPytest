# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: pytest配置文件 - BDD版本
# @Time   : 2026-04-17
# @Author : 毛鹏
"""
pytest配置文件 - BDD版本

此文件配置pytest-bdd测试环境
"""

# 导入原有的fixtures
from auto_tests.bdd_api_mock.fixtures.conftest import *


# pytest-bdd配置
def pytest_configure(config):
    """pytest配置"""
    # 添加BDD相关的markers
    config.addinivalue_line("markers", "smoke: 冒烟测试")
    config.addinivalue_line("markers", "positive: 正向测试")
    config.addinivalue_line("markers", "negative: 负向测试")
    config.addinivalue_line("markers", "integration: 集成测试")
    config.addinivalue_line("markers", "e2e: 端到端测试")
    config.addinivalue_line("markers", "bdd: BDD测试")

# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 测试支持模块 - 提供测试分层、上下文和报告功能
# @Time   : 2026-05-03
# @Author : 毛鹏
"""
测试支持模块

包含：
- 测试分层：UnitTest, IntegrationTest, E2ETest
- 测试上下文：TestContext, EventExpectation
- 报告功能：AllureAdapter
"""

from core.testing.layers import UnitTest, IntegrationTest, E2ETest, TestLayerType
from core.testing.context import TestContext, EventExpectation
from core.testing.reporting import AllureAdapter

__all__ = [
    # 测试分层
    'UnitTest',
    'IntegrationTest',
    'E2ETest',
    'TestLayerType',
    # 测试上下文
    'TestContext',
    'EventExpectation',
    # 报告
    'AllureAdapter',
]

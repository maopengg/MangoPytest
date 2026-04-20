# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 订单管理模块 BDD 测试
# @Time   : 2026-04-17
# @Author : 毛鹏
"""
订单管理模块 BDD 测试

此文件使用 pytest-bdd 运行 order.feature 中的场景
"""

from pytest_bdd import scenarios

# 加载 feature 文件
scenarios('order.feature')

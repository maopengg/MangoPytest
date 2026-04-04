# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 策略基类
# @Time   : 2026-04-01
# @Author : 毛鹏
"""
策略基类模块

注意：基类已从 core.base 导入，此类保留用于向后兼容
"""

# 从 core.base 导入基类
from core.base import BaseStrategy, StrategyResult

# 从统一的枚举文件导入
from core.enums.demo_enum import CreateStrategyAuto as CreateStrategy

__all__ = ['BaseStrategy', 'StrategyResult', 'CreateStrategy']

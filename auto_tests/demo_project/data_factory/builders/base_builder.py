# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: Builder基类 - 支持Strategy和自动依赖解决
# @Time   : 2026-04-01
# @Author : 毛鹏
"""
Builder基类模块

注意：基类已从 core.base 导入，此类保留用于向后兼容
"""

# 从 core.base 导入基类
from core.base import BaseBuilder, BuilderContext

# 从统一的枚举文件导入
from core.enums.demo_enum import DependencyLevel

__all__ = ['BaseBuilder', 'BuilderContext', 'DependencyLevel']

# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 实体基类 - 定义实体生命周期和通用行为
# @Time   : 2026-03-31
# @Author : 毛鹏
"""
实体基类模块

注意：基类已从 core.base 导入，此类保留用于向后兼容
"""

# 从 core.base 导入基类
from core.base import BaseEntity

# 从统一的枚举文件导入
from core.enums.demo_enum import EntityStatus

__all__ = ['BaseEntity', 'EntityStatus']

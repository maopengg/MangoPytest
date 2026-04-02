# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: Core Models - 共享数据模型
# @Time   : 2026-04-01
# @Author : 毛鹏

"""
Core Models 模块

提供共享的数据模型基类
"""

from .base import BaseModel
from .entity import BaseEntity
from .result import Result

__all__ = [
    "BaseModel",
    "BaseEntity",
    "Result",
]

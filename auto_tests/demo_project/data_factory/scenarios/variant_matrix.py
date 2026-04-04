# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 变体矩阵 - 向后兼容入口
# @Time   : 2026-04-01
# @Author : 毛鹏
"""
变体矩阵模块 - 向后兼容入口

注意：所有变体矩阵类已从 models.demo_model 导入
请使用新的导入方式：from models import VariantMatrix, Dimension, Variant
"""

# 从 models 导入所有变体矩阵相关类
from models import (
    Dimension,
    Variant,
    VariantMatrixResult,
    VariantMatrix,
    VariantExecutor,
)

# 从 enums 导入变体状态
from enums import VariantStatus

__all__ = [
    'VariantStatus',
    'Dimension',
    'Variant',
    'VariantMatrixResult',
    'VariantMatrix',
    'VariantExecutor',
]

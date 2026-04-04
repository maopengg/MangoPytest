# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 数据模型模块 - 包含所有项目数据模型定义
# @Time   : 2023-08-07 11:12
# @Author : 毛鹏

# 导出 demo_project 专用模型（方便使用方导入）
from core.models.demo_model import (
    # 配置相关
    BaseConfig, DevConfig, TestConfig, PreConfig, ProdConfig, CIConfig,
    Settings, get_settings, settings,
    # 策略相关
    StrategyResult,
    # Builder相关
    BuilderContext,
    # 血缘相关
    LineageEdge, DataLineageNode, LineagePath,
    # 变体矩阵相关
    Dimension, Variant, VariantMatrixResult,
    VariantMatrix, VariantExecutor,
)

__all__ = [
    # 配置
    'BaseConfig', 'DevConfig', 'TestConfig', 'PreConfig', 'ProdConfig', 'CIConfig',
    'Settings', 'get_settings', 'settings',
    # 策略
    'StrategyResult',
    # Builder
    'BuilderContext',
    # 血缘
    'LineageEdge', 'DataLineageNode', 'LineagePath',
    # 变体矩阵
    'Dimension', 'Variant', 'VariantMatrixResult',
    'VariantMatrix', 'VariantExecutor',
]

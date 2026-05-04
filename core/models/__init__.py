# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 数据模型模块 - 包含所有项目数据模型定义
# @Time   : 2023-08-07 11:12
# @Author : 毛鹏

# API 相关
from core.models.api import (
    APIResponse, ApiInfoModel, RequestModel, ResponseModel, ApiDataModel,
    json_serialize,
)
# 配置相关
from core.models.config import (
    BaseConfig, DevConfig, TestConfig, PreConfig, ProdConfig, CIConfig,
    Settings, get_settings, settings,
)
# 血缘相关
from core.models.lineage import (
    LineageEdge, DataLineageNode, LineagePath,
)
# 策略和 Builder 相关
from core.models.strategy import (
    StrategyResult, BuilderContext,
)
# 测试运行相关
from core.models.testrun import (
    CaseRunModel, TestMetrics, SurfaceModel, FeiShuModel,
    ProjectModel, TestObjectModel,
)
# 变体矩阵相关
from core.models.variant import (
    Dimension, Variant, VariantMatrixResult, VariantMatrix, VariantExecutor,
)

__all__ = [
    # 配置
    'BaseConfig', 'DevConfig', 'TestConfig', 'PreConfig', 'ProdConfig', 'CIConfig',
    'Settings', 'get_settings', 'settings',
    # API
    'APIResponse', 'ApiInfoModel', 'RequestModel', 'ResponseModel', 'ApiDataModel',
    'json_serialize',
    # 测试运行
    'CaseRunModel', 'TestMetrics', 'SurfaceModel', 'FeiShuModel',
    'ProjectModel', 'TestObjectModel',
    # 策略和 Builder
    'StrategyResult', 'BuilderContext',
    # 血缘
    'LineageEdge', 'DataLineageNode', 'LineagePath',
    # 变体矩阵
    'Dimension', 'Variant', 'VariantMatrixResult', 'VariantMatrix', 'VariantExecutor',
]

# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: Core 框架层 - 跨项目复用的核心组件
# @Time   : 2026-04-01
# @Author : 毛鹏

"""
Core 框架层

职责：
1. 提供跨项目复用的核心组件
2. 统一 API 客户端
3. 共享数据模型
4. 通用工具函数

"""


# 延迟导入避免循环依赖
def __getattr__(name):
    if name == "APIClient":
        from .api.client import APIClient
        return APIClient
    elif name == "BaseEntity":
        from .models.entity import BaseEntity
        return BaseEntity
    elif name == "BaseModel":
        from .models.base import BaseModel
        return BaseModel
    elif name == "Result":
        from .models.result import Result
        return Result
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


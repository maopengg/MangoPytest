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

目录结构：
    core/
    ├── __init__.py
    ├── api/                    # 统一 API 客户端
    │   ├── __init__.py
    │   ├── client.py          # 基础 API 客户端
    │   ├── auth.py            # 认证相关
    │   └── exceptions.py      # API 异常
    ├── models/                 # 共享数据模型
    │   ├── __init__.py
    │   ├── base.py            # 基础模型
    │   ├── entity.py          # 实体基类
    │   └── result.py          # 结果模型
    └── utils/                  # 通用工具
        ├── __init__.py
        ├── decorators.py      # 装饰器
        ├── helpers.py         # 辅助函数
        └── validators.py      # 验证器

使用示例：
    from auto_test.demo_project.core import APIClient
    from auto_test.demo_project.core.models import BaseEntity
    from auto_test.demo_project.core.utils import retry
"""

__version__ = "1.0.0"
__author__ = "毛鹏"

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


__all__ = [
    # API
    "APIClient",
    # Models
    "BaseEntity",
    "BaseModel",
    "Result",
    # Utils
    "retry",
    "validate",
    "timer",
]

# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: Core API 模块 - 统一 API 客户端
# @Time   : 2026-04-01
# @Author : 毛鹏

"""
Core API 模块

提供统一的 API 客户端和工具，支持：
1. HTTP 请求封装（GET/POST/PUT/DELETE）
2. 认证管理
3. 重试机制
4. 异常处理（使用全局异常类）
5. 请求/响应日志
6. 测试用例工具
7. HTTP 请求工具

异常处理：
    使用全局异常类：
    from core.exceptions import ApiError, ERROR_MSG_0400
    raise ApiError(*ERROR_MSG_0400.format("请求超时"))
"""

from .auth import AuthManager
from .client import APIClient
from .case_tool import CaseTool
from .request_tool import RequestTool

__all__ = [
    # 客户端和认证
    "APIClient",
    "AuthManager",
    # 工具类
    "CaseTool",
    "RequestTool",
]

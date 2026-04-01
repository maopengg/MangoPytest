# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: Core API 模块 - 统一 API 客户端
# @Time   : 2026-04-01
# @Author : 毛鹏

"""
Core API 模块

提供统一的 API 客户端，支持：
1. HTTP 请求封装（GET/POST/PUT/DELETE）
2. 认证管理
3. 重试机制
4. 异常处理
5. 请求/响应日志
"""

from .client import APIClient
from .auth import AuthManager
from .exceptions import APIException, AuthenticationException, RequestException

__all__ = [
    "APIClient",
    "AuthManager",
    "APIException",
    "AuthenticationException",
    "RequestException",
]

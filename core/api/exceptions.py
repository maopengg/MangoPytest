# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: Core API 异常 - 统一的异常处理
# @Time   : 2026-04-01
# @Author : 毛鹏

"""
Core API 异常模块

提供统一的 API 异常类
"""

from typing import Optional, Any


class APIException(Exception):
    """
    API 异常基类
    
    Attributes:
        message: 错误消息
        status_code: HTTP 状态码
        response_data: 响应数据
    """

    def __init__(
            self,
            message: str,
            status_code: Optional[int] = None,
            response_data: Optional[Any] = None
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_data = response_data

    def __str__(self) -> str:
        if self.status_code:
            return f"[{self.status_code}] {self.message}"
        return self.message


class AuthenticationException(APIException):
    """认证异常"""

    def __init__(self, message: str = "认证失败", **kwargs):
        super().__init__(message, status_code=401, **kwargs)


class RequestException(APIException):
    """请求异常"""

    def __init__(self, message: str = "请求失败", **kwargs):
        super().__init__(message, **kwargs)


class ValidationException(APIException):
    """验证异常"""

    def __init__(self, message: str = "数据验证失败", **kwargs):
        super().__init__(message, status_code=400, **kwargs)


class NotFoundException(APIException):
    """资源不存在异常"""

    def __init__(self, message: str = "资源不存在", **kwargs):
        super().__init__(message, status_code=404, **kwargs)


class ServerException(APIException):
    """服务器异常"""

    def __init__(self, message: str = "服务器错误", **kwargs):
        super().__init__(message, status_code=500, **kwargs)


__all__ = [
    "APIException",
    "AuthenticationException",
    "RequestException",
    "ValidationException",
    "NotFoundException",
    "ServerException",
]

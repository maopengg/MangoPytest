# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: API 请求 Allure 日志记录
# @Time   : 2026-04-03
# @Author : 毛鹏

"""
API 请求 Allure 日志记录模块

自动将 API 请求和响应信息记录到 Allure 报告，包括：
- 请求 URL
- 请求方式
- 请求头
- 请求数据（params/data/json/file）
- 响应结果
- 响应时间
- HTTP 状态码

使用示例：
    from pe.reporting.api_logger import api_allure_logger
    
    @api_allure_logger
    def test_api_call():
        response = client.get("/users")
        return response
"""

import functools
from typing import Any, Optional

import allure

from .adapter import AllureAdapter


def api_allure_logger(func):
    """
    API 请求 Allure 日志装饰器
    
    自动记录 API 请求和响应信息到 Allure 报告
    
    使用示例：
        @api_allure_logger
        def test_get_users():
            response = client.get("/users")
            return response
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # 执行原始函数
        response = func(*args, **kwargs)

        # 记录 API 请求信息到 Allure
        _log_api_request_to_allure(response)

        return response

    return wrapper


def _log_api_request_to_allure(response):
    """
    将 API 请求信息记录到 Allure
    
    @param response: APIResponse 对象
    """
    if not hasattr(response, '__dict__'):
        return

    # 获取请求信息（从 response 中或从上下文中）
    # 注意：这里假设 response 对象包含 request 信息
    # 实际使用时可能需要调整

    with AllureAdapter.step(f"API 请求: {getattr(response, 'method', 'UNKNOWN')} {getattr(response, 'url', '')}"):
        # 构建请求信息
        request_info = {
            "请求方式": getattr(response, 'method', 'UNKNOWN'),
            "请求URL": getattr(response, 'url', ''),
            "请求头": getattr(response, 'request_headers', {}),
        }

        # 添加请求数据（如果有）
        if hasattr(response, 'request_params') and response.request_params:
            request_info["请求Params"] = response.request_params
        if hasattr(response, 'request_data') and response.request_data:
            request_info["请求Data"] = response.request_data
        if hasattr(response, 'request_json') and response.request_json:
            request_info["请求JSON"] = response.request_json
        if hasattr(response, 'request_file') and response.request_file:
            request_info["请求文件"] = str(response.request_file)

        # 添加响应信息
        request_info["HTTP状态码"] = response.status_code
        request_info["响应时长(ms)"] = getattr(response, 'elapsed_ms', 0)

        # 附加到 Allure
        AllureAdapter.attach_json("API 请求详情", request_info)

        # 附加响应内容
        response_data = {
            "状态码": response.status_code,
            "响应数据": response.data if hasattr(response, 'data') else str(response),
            "响应头": getattr(response, 'headers', {}),
        }
        AllureAdapter.attach_json("API 响应详情", response_data)


class APIAllureMixin:
    """
    API Allure 日志 Mixin 类
    
    可以混入到 APIClient 中，自动记录所有请求到 Allure
    
    使用示例：
        class APIClient(APIAllureMixin):
            def get(self, path, **kwargs):
                response = self._do_request("GET", path, **kwargs)
                self._log_to_allure(response)  # 自动记录
                return response
    """

    def _log_request_to_allure(self, method: str, url: str, headers: dict,
                               params: Optional[dict] = None,
                               data: Optional[Any] = None,
                               response: Optional[Any] = None):
        """
        记录请求信息到 Allure
        
        @param method: 请求方式
        @param url: 请求 URL
        @param headers: 请求头
        @param params: 请求参数
        @param data: 请求数据
        @param response: 响应对象
        """
        with AllureAdapter.step(f"API 请求: {method} {url}"):
            # 请求信息
            request_info = {
                "请求方式": method,
                "请求URL": url,
                "请求头": headers,
            }

            if params:
                request_info["请求Params"] = params
            if data:
                request_info["请求数据"] = data

            AllureAdapter.attach_json("请求信息", request_info)

            # 响应信息
            if response:
                response_info = {
                    "HTTP状态码": response.status_code,
                    "响应时长(ms)": getattr(response, 'elapsed_ms', 0),
                    "响应数据": getattr(response, 'data', str(response)),
                }
                AllureAdapter.attach_json("响应信息", response_info)


def log_api_request(method: str, url: str, headers: dict,
                    params: Optional[dict] = None,
                    data: Optional[Any] = None,
                    response: Optional[Any] = None):
    """
    手动记录 API 请求到 Allure
    
    使用示例：
        response = client.get("/users")
        log_api_request("GET", "/users", headers, response=response)
    """
    with AllureAdapter.step(f"API 请求: {method} {url}"):
        # 请求信息
        request_info = {
            "请求方式": method,
            "请求URL": url,
            "请求头": headers,
        }

        if params:
            request_info["请求Params"] = params
        if data:
            request_info["请求数据"] = data

        AllureAdapter.attach_json("请求信息", request_info)

        # 响应信息
        if response:
            response_info = {
                "HTTP状态码": response.status_code,
                "响应时长(ms)": getattr(response, 'elapsed_ms', 0),
                "响应数据": getattr(response, 'data', str(response)),
            }
            AllureAdapter.attach_json("响应信息", response_info)

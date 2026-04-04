# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: Core API 客户端 - 统一 HTTP 请求封装
# @Time   : 2026-04-01
# @Author : 毛鹏

"""
Core API 客户端

统一的 HTTP 请求封装，支持：
- GET/POST/PUT/DELETE 请求
- 自动重试机制
- 请求/响应拦截
- 统一的错误处理
- 请求/响应日志打印
- Allure 报告集成

使用 httpx 库实现，支持同步和异步请求

注意：APIResponse 和 api_allure_logger 已从 models.api_model 和 core.decorators 导入
"""

import time
from typing import Dict, Any, Optional, Callable, List

import httpx

from tools.log import log
from models.api_model import APIResponse
from core.decorators import api_allure_logger, _log_api_response_to_allure


class APIClient:
    """
    统一 API 客户端

    使用示例：
        client = APIClient(base_url="https://api.example.com")
        client.set_auth_token("your_token")

        # GET 请求
        response = client.get("/users")

        # POST 请求
        response = client.post("/users", {"name": "test"})

        # 带重试的请求
        response = client.get("/users", retry_count=3, retry_delay=1.0)
        
        # 使用上下文管理器
        with APIClient(base_url="https://api.example.com") as client:
            response = client.get("/users")
    """

    def __init__(
            self,
            base_url: str = "",
            timeout: int = 30,
            headers: Optional[Dict[str, str]] = None,
            auth_token: Optional[str] = None,
            enable_allure: bool = True,
    ):
        """
        初始化 API 客户端

        @param base_url: 基础 URL
        @param timeout: 超时时间(秒)
        @param headers: 默认请求头
        @param auth_token: 认证 token
        @param enable_allure: 是否启用 Allure 日志记录
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.headers = headers or {}
        self.auth_token = auth_token
        self.enable_allure = enable_allure

        # 请求/响应拦截器
        self._request_interceptors: List[Callable] = []
        self._response_interceptors: List[Callable] = []

        # 统计信息
        self._request_count = 0
        self._error_count = 0

        # 创建 httpx 客户端
        self._client = httpx.Client(timeout=timeout)

    def set_auth_token(self, token: str):
        """设置认证 token"""
        self.auth_token = token

    def set_base_url(self, base_url: str):
        """设置基础 URL"""
        self.base_url = base_url.rstrip("/")

    def add_request_interceptor(self, interceptor: Callable):
        """添加请求拦截器"""
        self._request_interceptors.append(interceptor)

    def add_response_interceptor(self, interceptor: Callable):
        """添加响应拦截器"""
        self._response_interceptors.append(interceptor)

    def _build_url(self, path: str) -> str:
        """构建完整 URL"""
        path = path.lstrip("/")
        return f"{self.base_url}/{path}"

    def _build_headers(
            self, extra_headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, str]:
        """构建请求头"""
        headers = self.headers.copy()
        headers["Content-Type"] = "application/json"
        headers["Accept"] = "application/json"

        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"

        if extra_headers:
            headers.update(extra_headers)

        return headers

    def _do_request(
            self,
            method: str,
            url: str,
            headers: Dict[str, str],
            data: Optional[Any] = None,
            params: Optional[Dict[str, Any]] = None,
    ) -> APIResponse:
        """
        执行 HTTP 请求

        @param method: HTTP 方法
        @param url: 请求 URL
        @param headers: 请求头
        @param data: 请求数据
        @param params: 查询参数
        @return: API 响应
        """

        start_time = time.time()

        try:
            # 使用 httpx 发送请求
            if method == "GET":
                response = self._client.get(url, headers=headers, params=params)
            elif method == "POST":
                response = self._client.post(url, headers=headers, json=data)
            elif method == "PUT":
                response = self._client.put(url, headers=headers, json=data)
            elif method == "DELETE":
                response = self._client.delete(url, headers=headers)
            else:
                raise RequestException(f"不支持的 HTTP 方法: {method}")

            elapsed_ms = (time.time() - start_time) * 1000

            # 解析响应数据
            try:
                response_data = response.json()
            except Exception as e:
                log.info(f'解析json格式数据错误：{e}')
                response_data = response.text

            api_response = APIResponse(
                status_code=response.status_code,
                data=response_data,
                headers=dict(response.headers),
                elapsed_ms=elapsed_ms,
                request_method=method,
                request_url=url,
                request_headers=headers,
                request_params=params,
                request_data=data,
            )

            return api_response

        except httpx.RequestError as e:
            print(f"请求异常: {str(e)}")
            print(f"{'=' * 100}\n")
            raise RequestException(f"请求失败: {str(e)}")

    def request(
            self,
            method: str,
            path: str,
            data: Optional[Any] = None,
            params: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None,
            retry_count: int = 0,
            retry_delay: float = 1.0,
    ) -> APIResponse:
        """
        发送 HTTP 请求

        @param method: HTTP 方法
        @param path: 请求路径
        @param data: 请求数据
        @param params: 查询参数
        @param headers: 额外请求头
        @param retry_count: 重试次数
        @param retry_delay: 重试延迟(秒)
        @return: API 响应
        """
        url = self._build_url(path)
        request_headers = self._build_headers(headers)

        # 执行请求拦截器
        for interceptor in self._request_interceptors:
            method, url, request_headers, data = interceptor(
                method, url, request_headers, data
            )

        self._request_count += 1

        last_error = None
        for attempt in range(retry_count + 1):
            try:
                response = self._do_request(method, url, request_headers, data, params)

                # 执行响应拦截器
                for interceptor in self._response_interceptors:
                    response = interceptor(response)

                # 检查响应状态
                if response.is_error:
                    raise APIException(
                        f"API 错误: {response.status_code}",
                        status_code=response.status_code,
                        response_data=response.data,
                    )

                # 记录到 Allure
                if self.enable_allure:
                    _log_api_response_to_allure(response)

                return response

            except Exception as e:
                last_error = e
                if attempt < retry_count:
                    time.sleep(retry_delay)
                    continue
                else:
                    self._error_count += 1
                    raise

        raise last_error or RequestException("请求失败")

    @api_allure_logger
    def get(
            self, path: str, params: Optional[Dict[str, Any]] = None, **kwargs
    ) -> APIResponse:
        """GET 请求"""
        return self.request("GET", path, params=params, **kwargs)

    @api_allure_logger
    def post(self, path: str, data: Optional[Any] = None, **kwargs) -> APIResponse:
        """POST 请求"""
        return self.request("POST", path, data=data, **kwargs)

    @api_allure_logger
    def put(self, path: str, data: Optional[Any] = None, **kwargs) -> APIResponse:
        """PUT 请求"""
        return self.request("PUT", path, data=data, **kwargs)

    @api_allure_logger
    def delete(self, path: str, **kwargs) -> APIResponse:
        """DELETE 请求"""
        return self.request("DELETE", path, **kwargs)

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "request_count": self._request_count,
            "error_count": self._error_count,
            "success_rate": 1.0 - (self._error_count / max(self._request_count, 1)),
        }

    def close(self):
        """关闭客户端"""
        self._client.close()

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        self.close()

# -*- coding: utf-8 -*-
"""
API 客户端 - 集成 core APIClient 功能

在保持 BDD 测试兼容性的同时，集成 core APIClient 的功能：
- 占位符替换 (${entity.id})
- 自动重试机制
- 请求/响应拦截器
- 统一的错误处理
- 请求/响应日志打印
- Allure 报告集成
- 连接池管理
"""

import json
import re
import time
from typing import Any, Dict, Optional, Callable, List

import httpx
import allure

from auto_tests.bdd_api_mock.config import settings
from core.utils import log


class APIResponse:
    """API 响应数据类 - 兼容 BDD 测试的 Dict 格式，同时提供 core APIResponse 的功能"""

    def __init__(
        self,
        status_code: int,
        data: Any,
        headers: Dict[str, str],
        elapsed_ms: float,
        request_method: str = "",
        request_url: str = "",
        request_headers: Dict[str, Any] = None,
        request_params: Optional[Dict[str, Any]] = None,
        request_data: Optional[Any] = None,
    ):
        self.status_code = status_code
        self.data = data
        self.headers = headers
        self.elapsed_ms = elapsed_ms
        self.request_method = request_method
        self.request_url = request_url
        self.request_headers = request_headers or {}
        self.request_params = request_params
        self.request_data = request_data

    @property
    def is_success(self) -> bool:
        """是否成功响应 (2xx)"""
        return 200 <= self.status_code < 300

    @property
    def is_error(self) -> bool:
        """是否错误响应"""
        return not self.is_success

    def to_dict(self) -> Dict[str, Any]:
        """转换为 BDD 测试期望的 Dict 格式"""
        # 如果 data 已经是 dict 且包含 code/data/message，直接返回
        if isinstance(self.data, dict):
            if "code" in self.data and "data" in self.data:
                return self.data
        # 否则包装成标准格式
        return {
            "code": self.status_code,
            "data": self.data,
            "message": "success" if self.is_success else f"HTTP {self.status_code}",
        }

    def __getitem__(self, key: str) -> Any:
        """支持 Dict 风格的访问"""
        return self.to_dict()[key]

    def __contains__(self, key: str) -> bool:
        """支持 in 操作符"""
        return key in self.to_dict()

    def get(self, key: str, default: Any = None) -> Any:
        """支持 Dict 风格的 get 方法"""
        return self.to_dict().get(key, default)


class APIClient:
    """增强版 API 客户端 - 集成 core 功能，保持 BDD 兼容性"""

    def __init__(
        self,
        base_url: str = None,
        timeout: int = 30,
        headers: Optional[Dict[str, str]] = None,
        pool_connections: int = 10,
        pool_maxsize: int = 10,
    ):
        """
        初始化 API 客户端

        @param base_url: 基础 URL
        @param timeout: 超时时间(秒)
        @param headers: 默认请求头
        @param pool_connections: 连接池连接数
        @param pool_maxsize: 连接池最大连接数
        """
        self.base_url = (base_url or settings.BASE_URL).rstrip("/")
        self.timeout = timeout
        self.headers = headers or {}
        self.token = None

        # 请求/响应拦截器
        self._request_interceptors: List[Callable] = []
        self._response_interceptors: List[Callable] = []

        # 统计信息
        self._request_count = 0
        self._error_count = 0

        # 创建 httpx 客户端，配置连接池
        limits = httpx.Limits(
            max_connections=pool_maxsize,
            max_keepalive_connections=pool_connections,
        )
        self._client = httpx.Client(timeout=timeout, limits=limits)

    def set_token(self, token: str):
        """设置认证令牌"""
        self.token = token
        self.headers["Authorization"] = f"Bearer {token}"
        self.headers["X-Token"] = token

    def add_request_interceptor(self, interceptor: Callable):
        """添加请求拦截器"""
        self._request_interceptors.append(interceptor)

    def add_response_interceptor(self, interceptor: Callable):
        """添加响应拦截器"""
        self._response_interceptors.append(interceptor)

    def _prepare_url(self, path: str, created_entity=None) -> str:
        """准备 URL，替换占位符"""
        url = path if path.startswith("http") else f"{self.base_url}/{path.lstrip('/')}"

        # 替换占位符 ${entity.id}
        if created_entity is not None:
            url = re.sub(r"\$\{(\w+)\.id\}", str(created_entity.id), url)

        return url

    def _prepare_body(self, body: Dict, created_entity=None) -> Dict:
        """准备请求体，替换占位符"""
        if created_entity is None:
            return body

        body_str = json.dumps(body)
        body_str = re.sub(r"\$\{(\w+)\.id\}", str(created_entity.id), body_str)
        return json.loads(body_str)

    def _log_to_allure(
        self,
        method: str,
        url: str,
        headers: Dict,
        params: Optional[Dict],
        data: Optional[Any],
        response: APIResponse,
    ):
        """记录请求和响应信息到 Allure 报告"""
        try:
            with allure.step(f"API 请求: {method} {url}"):
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

                allure.attach(
                    json.dumps(request_info, ensure_ascii=False, indent=2),
                    "请求详情",
                    allure.attachment_type.JSON,
                )

                # 响应信息
                response_info = {
                    "HTTP状态码": response.status_code,
                    "响应时长(ms)": round(response.elapsed_ms, 2),
                    "响应数据": response.data,
                }
                allure.attach(
                    json.dumps(response_info, ensure_ascii=False, indent=2),
                    "响应详情",
                    allure.attachment_type.JSON,
                )
        except Exception as e:
            log.warning(f"Allure 日志记录失败: {e}")

    def _do_request(
        self,
        method: str,
        url: str,
        headers: Dict[str, str],
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Any] = None,
    ) -> APIResponse:
        """执行 HTTP 请求"""
        start_time = time.time()

        # 合并请求头
        request_headers = {**self.headers, **headers}

        # 执行请求拦截器
        for interceptor in self._request_interceptors:
            method, url, request_headers, json_data = interceptor(
                method, url, request_headers, json_data
            )

        # 发送请求
        response = self._client.request(
            method=method,
            url=url,
            headers=request_headers,
            params=params,
            json=json_data,
        )

        elapsed_ms = (time.time() - start_time) * 1000

        # 解析响应数据
        try:
            response_data = response.json()
        except json.JSONDecodeError:
            response_data = response.text

        api_response = APIResponse(
            status_code=response.status_code,
            data=response_data,
            headers=dict(response.headers),
            elapsed_ms=elapsed_ms,
            request_method=method,
            request_url=url,
            request_headers=request_headers,
            request_params=params,
            request_data=json_data,
        )

        # 执行响应拦截器
        for interceptor in self._response_interceptors:
            api_response = interceptor(api_response)

        return api_response

    def request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
        created_entity=None,
        retry_count: int = 0,
        retry_delay: float = 1.0,
    ) -> APIResponse:
        """
        发送 HTTP 请求

        @param method: HTTP 方法
        @param path: 请求路径
        @param params: 查询参数
        @param json_data: JSON 数据
        @param headers: 额外请求头
        @param created_entity: 用于占位符替换的实体
        @param retry_count: 重试次数
        @param retry_delay: 重试延迟(秒)
        @return: APIResponse 对象
        """
        url = self._prepare_url(path, created_entity)
        json_data = self._prepare_body(json_data or {}, created_entity)
        request_headers = headers or {}

        self._request_count += 1

        last_error = None
        for attempt in range(retry_count + 1):
            try:
                response = self._do_request(
                    method=method,
                    url=url,
                    headers=request_headers,
                    params=params,
                    json_data=json_data,
                )

                # 记录到 Allure
                self._log_to_allure(
                    method, url, request_headers, params, json_data, response
                )

                if response.is_error:
                    log.warning(f"请求失败: HTTP {response.status_code}")

                return response

            except Exception as e:
                last_error = e
                if attempt < retry_count:
                    log.warning(f"请求失败，{retry_delay}秒后重试: {e}")
                    time.sleep(retry_delay)
                    continue
                else:
                    self._error_count += 1
                    log.error(f"请求失败，已重试{retry_count}次: {e}")
                    raise

        raise last_error

    def get(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        created_entity=None,
        **kwargs,
    ) -> Dict[str, Any]:
        """GET 请求 - 返回 Dict 格式保持 BDD 兼容性"""
        response = self.request(
            "GET", path, params=params, created_entity=created_entity, **kwargs
        )
        return response.to_dict()

    def post(
        self,
        path: str,
        body: Optional[Dict] = None,
        created_entity=None,
        **kwargs,
    ) -> Dict[str, Any]:
        """POST 请求 - 返回 Dict 格式保持 BDD 兼容性"""
        response = self.request(
            "POST", path, json_data=body, created_entity=created_entity, **kwargs
        )
        return response.to_dict()

    def put(
        self,
        path: str,
        body: Optional[Dict] = None,
        created_entity=None,
        **kwargs,
    ) -> Dict[str, Any]:
        """PUT 请求 - 返回 Dict 格式保持 BDD 兼容性"""
        response = self.request(
            "PUT", path, json_data=body, created_entity=created_entity, **kwargs
        )
        return response.to_dict()

    def delete(self, path: str, created_entity=None, **kwargs) -> Dict[str, Any]:
        """DELETE 请求 - 返回 Dict 格式保持 BDD 兼容性"""
        response = self.request("DELETE", path, created_entity=created_entity, **kwargs)
        return response.to_dict()

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
        log.debug("APIClient 已关闭")

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        self.close()

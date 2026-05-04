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

import json
import os
import re
import time
import uuid
from typing import Dict, Any, Optional, Callable, List

import httpx

from core.utils import log
from core.models import APIResponse
from core.decorators import api_allure_logger
from core.exceptions import ApiError


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
        pool_connections: int = 10,
        pool_maxsize: int = 10,
        verify: bool = True,
    ):
        """
        初始化 API 客户端

        @param base_url: 基础 URL
        @param timeout: 超时时间(秒)
        @param headers: 默认请求头
        @param pool_connections: 连接池连接数
        @param pool_maxsize: 连接池最大连接数
        @param verify: 是否验证SSL证书，默认True
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.headers = headers or {}
        self.verify = verify

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
        self._client = httpx.Client(
            timeout=timeout, limits=limits, verify=verify, trust_env=False
        )

    def set_base_url(self, base_url: str):
        """设置基础 URL"""
        self.base_url = base_url.rstrip("/")

    def add_request_interceptor(self, interceptor: Callable):
        """添加请求拦截器"""
        self._request_interceptors.append(interceptor)

    def add_response_interceptor(self, interceptor: Callable):
        """添加响应拦截器"""
        self._response_interceptors.append(interceptor)

    def _build_url(self, path: str, context: Optional[Dict[str, Any]] = None) -> str:
        """构建完整 URL

        @param path: 请求路径
        @param context: 上下文数据，用于替换 ${{key}} 占位符
        @return: 完整 URL
        """
        # 替换 ${{key}} 占位符
        if context:
            for key, value in context.items():
                path = re.sub(rf"\$\{{\{{{key}\}}\}}", str(value), path)

        path = path.lstrip("/")
        return f"{self.base_url}/{path}"

    def _do_request(
        self,
        method: str,
        url: str,
        headers: Dict[str, str],
        data: Optional[Any] = None,
        json_data: Optional[Any] = None,
        params: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> APIResponse:
        """
        执行 HTTP 请求

        @param method: HTTP 方法
        @param url: 请求 URL
        @param headers: 请求头
        @param data: 表单数据或文件上传时的附加数据
        @param json_data: JSON 数据
        @param params: 查询参数
        @param files: 文件上传参数
        @return: API 响应
        """

        start_time = time.time()

        # 使用 httpx 发送请求
        if files:
            headers.pop("Content-Type", None)
        response = self._client.request(
            method,
            url,
            headers=headers,
            data=data if files else None,
            files=files,
            params=params if not files else None,
            json=json_data if not files else None,
        )
        elapsed_ms = (time.time() - start_time) * 1000

        # 检测是否为文件下载响应
        content_type = response.headers.get("content-type", "").lower()
        content_disposition = response.headers.get("content-disposition", "").lower()
        is_file_response = (
            "application/octet-stream" in content_type
            or "application/pdf" in content_type
            or "application/vnd" in content_type  # Excel, Word 等
            or "image/" in content_type
            or "attachment" in content_disposition
        )

        if is_file_response:
            # 文件下载：保存到 download 目录
            from core.utils.project_dir import project_dir

            download_dir = project_dir.download()

            # 从 Content-Disposition 中提取文件名
            filename = None
            if "filename=" in content_disposition:
                match = re.search(r'filename="?([^"]+)"?', content_disposition)
                if match:
                    filename = match.group(1)

            # 如果无法提取文件名，使用 UUID 生成
            if not filename:
                # 从 URL 路径获取扩展名
                url_path = url.split("?")[0]  # 移除查询参数
                ext = ".bin"
                if "." in url_path:
                    ext = "." + url_path.split(".")[-1]
                filename = f"download_{uuid.uuid4().hex[:8]}{ext}"

            file_path = os.path.join(download_dir, filename)

            # 保存文件
            with open(file_path, "wb") as f:
                f.write(response.content)

            log.info(f"文件已下载: {file_path}")

            api_response = APIResponse(
                status_code=response.status_code,
                data=file_path,  # data 为文件路径
                headers=dict(response.headers),
                elapsed_ms=elapsed_ms,
                request_method=method,
                request_url=url,
                request_headers=headers,
                request_params=params,
                request_data=data,
                file_path=file_path,  # 有值表示是文件响应
            )
        else:
            # 普通响应：解析 JSON 或文本
            try:
                response_data = response.json()
            except Exception as e:
                log.info(f"解析json格式数据错误：{e}")
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

    @api_allure_logger
    def request(
        self,
        method: str,
        path: str,
        data: Optional[Any] = None,
        json_data: Optional[Any] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        files: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
        retry_count: int = 0,
        retry_delay: float = 1.0,
        raise_on_error: bool = True,
    ) -> APIResponse:
        """
        发送 HTTP 请求

        @param method: HTTP 方法
        @param path: 请求路径，支持 ${{key}} 占位符
        @param data: 表单数据或文件上传时的附加数据
        @param json_data: JSON 数据，支持 ${{key}} 占位符
        @param params: 查询参数
        @param headers: 请求头
        @param files: 文件上传参数
        @param context: 上下文数据，用于替换 ${{key}} 占位符
        @param retry_count: 重试次数
        @param retry_delay: 重试延迟(秒)
        @return: API 响应
        """
        # 处理 JSON 数据：如果是字符串，先替换占位符再解析
        if json_data is not None:
            if isinstance(json_data, str):
                # 替换占位符
                if context:
                    for key, value in context.items():
                        json_data = re.sub(
                            rf"\$\{{\{{{key}\}}\}}", str(value), json_data
                        )
                # 解析 JSON 字符串
                json_data = json.loads(json_data) if json_data.strip() else None
            elif context:
                # 如果是 dict 且有 context，序列化后替换再解析
                json_str = json.dumps(json_data)
                for key, value in context.items():
                    json_str = re.sub(rf"\$\{{\{{{key}\}}\}}", str(value), json_str)
                json_data = json.loads(json_str)

        url = self._build_url(path, context)
        # 合并默认headers和传入的headers（传入的headers优先级更高）
        request_headers = self.headers.copy()
        if headers:
            request_headers.update(headers)

        # 执行请求拦截器
        for interceptor in self._request_interceptors:
            method, url, request_headers, data = interceptor(
                method, url, request_headers, data
            )

        self._request_count += 1

        last_error = None
        for attempt in range(retry_count + 1):
            try:
                response = self._do_request(
                    method, url, request_headers, data, json_data, params, files
                )

                # 执行响应拦截器
                for interceptor in self._response_interceptors:
                    response = interceptor(response)

                # 检查响应状态
                if response.is_error and raise_on_error:
                    raise ApiError(
                        response.status_code,
                        f"API 错误: {response.status_code}，数据：{str(response.data)}",
                    )

                return response

            except Exception as e:
                last_error = e
                if attempt < retry_count:
                    time.sleep(retry_delay)
                    continue
                else:
                    self._error_count += 1
                    raise

        raise last_error

    def get(
        self, path: str, params: Optional[Dict[str, Any]] = None, **kwargs
    ) -> APIResponse:
        """GET 请求"""
        return self.request("GET", path, params=params, **kwargs)

    def post(self, path: str, json_data: Optional[Any] = None, **kwargs) -> APIResponse:
        """POST 请求"""
        return self.request("POST", path, json_data=json_data, **kwargs)

    def put(self, path: str, json_data: Optional[Any] = None, **kwargs) -> APIResponse:
        """PUT 请求"""
        return self.request("PUT", path, json_data=json_data, **kwargs)

    def delete(self, path: str, **kwargs) -> APIResponse:
        """DELETE 请求"""
        return self.request("DELETE", path, **kwargs)

    def upload(
        self,
        path: str,
        file_path: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> APIResponse:
        """
        文件上传

        @param path: 上传路径
        @param file_path: 本地文件路径
        @param data: 额外表单数据
        @param headers: 请求头
        @return: API 响应

        使用示例：
            response = client.upload("/upload", "/path/to/file.pdf")
            response = client.upload("/upload", "/path/to/file.pdf", data={"folder": "docs"})
        """
        with open(file_path, "rb") as f:
            files = {"file": (file_path.split("/")[-1].split("\\")[-1], f)}
            return self.request(
                "POST", path, data=data, files=files, headers=headers, **kwargs
            )

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

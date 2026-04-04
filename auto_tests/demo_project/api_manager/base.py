# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: Demo Project API 基类 - 带 token 拦截器
# @Time   : 2026-04-04
# @Author : 毛鹏

from typing import Optional
from core.api.client import APIClient


class DemoProjectBaseAPI:
    """Demo Project API 基类 - 共享 client 和 token"""

    _shared_client: Optional[APIClient] = None
    _host: str = "http://localhost:8003"
    _token: Optional[str] = None

    def __init__(self):
        pass

    def _get_client(self) -> APIClient:
        """获取或创建共享的 APIClient 实例"""
        if DemoProjectBaseAPI._shared_client is None:
            client = APIClient(base_url=self._host)
            client.add_request_interceptor(self._auth_interceptor)
            DemoProjectBaseAPI._shared_client = client
        return DemoProjectBaseAPI._shared_client

    @classmethod
    def set_token(cls, token: str):
        """设置全局认证 token"""
        cls._token = token

    @classmethod
    def clear_token(cls):
        """清除全局认证 token"""
        cls._token = None

    @classmethod
    def _auth_interceptor(cls, method: str, url: str, headers: dict, data: any):
        """请求拦截器 - 自动添加认证 token"""
        if cls._token:
            headers["Authorization"] = f"Bearer {cls._token}"
        return method, url, headers, data

    @classmethod
    def set_host(cls, host: str):
        """设置全局 API 服务器地址"""
        cls._host = host.rstrip("/")
        if cls._shared_client is not None:
            cls._shared_client.set_base_url(cls._host)

    @property
    def client(self) -> APIClient:
        """获取当前 APIClient 实例"""
        return self._get_client()

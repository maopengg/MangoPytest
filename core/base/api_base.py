# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: API 基础类 - 共享 APIClient
# @Time   : 2026-04-04
# @Author : 毛鹏

from typing import Optional
from core.api.client import APIClient


class BaseAPI:
    """API 基础类 - 共享 APIClient 实例"""

    _client: Optional[APIClient] = None
    _host: str = "http://localhost:8003"

    def __init__(self):
        if BaseAPI._client is None:
            BaseAPI._client = APIClient(base_url=self._host)

    @classmethod
    def set_host(cls, host: str):
        """设置全局 API 服务器地址"""
        cls._host = host.rstrip("/")
        if cls._client is not None:
            cls._client.set_base_url(cls._host)

    @classmethod
    def get_client(cls) -> APIClient:
        """获取共享的 APIClient 实例"""
        if cls._client is None:
            cls._client = APIClient(base_url=cls._host)
        return cls._client

    @property
    def client(self) -> APIClient:
        """获取当前 APIClient 实例"""
        return self.get_client()

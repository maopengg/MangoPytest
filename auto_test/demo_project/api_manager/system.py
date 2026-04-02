# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 系统API - 使用 Core APIClient
# @Time   : 2026-01-18 13:58
# @Author : 毛鹏

from auto_test.demo_project.core.api.client import APIClient


class SystemAPI:
    """系统API - 对应 /health, /info 接口"""

    def __init__(self):
        self._client = APIClient(base_url="http://localhost:8003")

    def set_host(self, host: str):
        """设置API服务器地址"""
        self._client.set_base_url(host)

    def set_token(self, token: str):
        """设置认证token"""
        self._client.set_auth_token(token)

    def health_check(self) -> dict:
        """
        健康检查接口
        GET /health
        @return: 响应字典
        """
        response = self._client.get("/health")
        return response.data

    def get_server_info(self) -> dict:
        """
        获取服务器信息接口
        GET /info
        @return: 响应字典
        """
        response = self._client.get("/info")
        return response.data

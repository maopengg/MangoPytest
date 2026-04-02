# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 数据API - 使用 Core APIClient
# @Time   : 2026-01-18 13:57
# @Author : 毛鹏

from core.api.client import APIClient


class DataAPI:
    """数据API - 对应 /api/data 接口"""

    def __init__(self):
        self._client = APIClient(base_url="http://localhost:8003")

    def set_host(self, host: str):
        """设置API服务器地址"""
        self._client.set_base_url(host)

    def set_token(self, token: str):
        """设置认证token"""
        self._client.set_auth_token(token)

    def submit_data(self, name: str, value: int) -> dict:
        """
        提交数据接口
        POST /api/data
        @param name: 数据名称
        @param value: 数据值
        @return: 响应字典
        """
        response = self._client.post("/api/data", data={"name": name, "value": value})
        return response.data

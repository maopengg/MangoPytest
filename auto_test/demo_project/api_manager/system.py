# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description:
# @Time   : 2026-01-18 13:58
# @Author : 毛鹏
from urllib.parse import urljoin

import requests


class SystemAPI:
    """系统API - 对应 /health, /info 接口"""

    def __init__(self):
        self._host = "http://localhost:8003"

    def set_host(self, host: str):
        """设置API服务器地址"""
        self._host = host.rstrip("/")

    def _get_url(self, path: str) -> str:
        """获取完整URL"""
        return urljoin(self._host + "/", path)

    def health_check(self) -> dict:
        """
        健康检查接口
        GET /health
        @return: 响应字典
        """
        url = self._get_url("health")
        response = requests.get(url)
        return response.json()

    def get_server_info(self) -> dict:
        """
        获取服务器信息接口
        GET /info
        @return: 响应字典
        """
        url = self._get_url("info")
        response = requests.get(url)
        return response.json()

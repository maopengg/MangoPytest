# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description:
# @Time   : 2026-01-18 13:57
# @Author : 毛鹏
from urllib.parse import urljoin

import requests


class DataAPI:
    """数据API - 对应 /api/data 接口"""

    def __init__(self):
        self._host = "http://localhost:8003"

    def set_host(self, host: str):
        """设置API服务器地址"""
        self._host = host.rstrip("/")

    def _get_url(self, path: str) -> str:
        """获取完整URL"""
        return urljoin(self._host + "/", path)

    def submit_data(self, name: str, value: str) -> dict:
        """
        提交数据接口
        POST /api/data
        @param name: 数据名称
        @param value: 数据值
        @return: 响应字典
        """
        url = self._get_url("api/data")
        response = requests.post(url, json={"name": name, "value": value})
        return response.json()

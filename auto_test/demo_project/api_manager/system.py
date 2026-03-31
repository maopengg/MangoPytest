# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2026-01-18 13:58
# @Author : 毛鹏
from urllib.parse import urljoin

from models.api_model import ApiDataModel
from tools.base_request.request_tool import RequestTool
from tools.decorator.response import request_data


class SystemAPI(RequestTool):
    """系统API - 对应 /health, /info 接口"""

    def __init__(self):
        super().__init__()
        self._host = "http://localhost:8003"

    def set_host(self, host: str):
        """设置API服务器地址"""
        self._host = host.rstrip('/')

    def _get_url(self, path: str) -> str:
        """获取完整URL"""
        return urljoin(self._host + "/", path)

    def health_check(self, data: ApiDataModel) -> ApiDataModel:
        """
        健康检查接口
        GET /health
        @param data: ApiDataModel
        @return: ApiDataModel
        """
        data.request.url = self._get_url("health")
        return self.http(data)

    def get_server_info(self, data: ApiDataModel) -> ApiDataModel:
        """
        获取服务器信息接口
        GET /info
        @param data: ApiDataModel
        @return: ApiDataModel
        """
        data.request.url = self._get_url("info")
        return self.http(data)

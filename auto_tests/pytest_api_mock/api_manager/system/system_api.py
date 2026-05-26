# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 系统API - 使用 Core APIClient
# @Time   : 2026-01-18 13:58
# @Author : 毛鹏

from ..base import DemoProjectBaseAPI


class SystemAPI(DemoProjectBaseAPI):
    """系统API - 对应 /health, /info 接口"""

    CUSTOM_HEADERS = {
        "X-Custom-Key": "mango_secret_key",
        "X-Request-Source": "pytest_api_mock",
    }

    def health_check(self, headers: dict = None, with_custom_headers: bool = True) -> dict:
        """
        健康检查接口
        GET /health
        @return: 响应字典
        """
        request_headers = {}
        if with_custom_headers:
            request_headers.update(self.CUSTOM_HEADERS)
        if headers:
            request_headers.update(headers)
        response = self.client.get("/health", headers=request_headers)
        return response.data

    def get_server_info(self, headers: dict = None, with_custom_headers: bool = True) -> dict:
        """
        获取服务器信息接口
        GET /info
        @return: 响应字典
        """
        request_headers = {}
        if with_custom_headers:
            request_headers.update(self.CUSTOM_HEADERS)
        if headers:
            request_headers.update(headers)
        response = self.client.get("/info", headers=request_headers)
        return response.data

    def startup(self) -> dict:
        """初始化数据接口 GET /startup。"""
        response = self.client.get("/startup")
        return response.data

    def home(self):
        """首页接口 GET /，返回APIResponse。"""
        return self.client.get("/")

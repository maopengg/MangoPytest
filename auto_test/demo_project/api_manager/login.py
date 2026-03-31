# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-03-17 19:50
# @Author : 毛鹏
from urllib.parse import urljoin

from models.api_model import ApiDataModel
from tools.base_request.request_tool import RequestTool
from tools.decorator.response import request_data


class LoginAPI(RequestTool):
    """登录API - 对应 /auth/login 接口"""

    def __init__(self):
        super().__init__()
        self._host = "http://localhost:8003"

    def set_host(self, host: str):
        """设置API服务器地址"""
        self._host = host.rstrip('/')

    def _get_url(self, path: str) -> str:
        """获取完整URL"""
        return urljoin(self._host + "/", path)

    def api_login(self, data: ApiDataModel) -> ApiDataModel:
        """
        登录接口
        POST /auth/login
        @param data: ApiDataModel (包含 username, password)
        @return: ApiDataModel
        """
        data.request.url = self._get_url("auth/login")
        return self.http(data)

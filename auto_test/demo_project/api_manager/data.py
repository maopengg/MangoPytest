# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2026-01-18 13:57
# @Author : 毛鹏
from urllib.parse import urljoin

from models.api_model import ApiDataModel
from tools.base_request.request_tool import RequestTool
from tools.decorator.response import request_data


class DataAPI(RequestTool):
    """数据API - 对应 /api/data 接口"""

    def __init__(self):
        super().__init__()
        self._host = "http://localhost:8003"

    def set_host(self, host: str):
        """设置API服务器地址"""
        self._host = host.rstrip('/')

    def _get_url(self, path: str) -> str:
        """获取完整URL"""
        return urljoin(self._host + "/", path)

    def submit_data(self, data: ApiDataModel) -> ApiDataModel:
        """
        提交数据接口
        POST /api/data
        @param data: ApiDataModel (包含 name, value)
        @return: ApiDataModel
        """
        data.request.url = self._get_url("api/data")
        return self.http(data)

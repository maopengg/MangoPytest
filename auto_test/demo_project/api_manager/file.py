# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2026-01-18 13:57
# @Author : 毛鹏
from urllib.parse import urljoin

from models.api_model import ApiDataModel
from tools.base_request.request_tool import RequestTool
from tools.decorator.response import request_data


class FileAPI(RequestTool):
    """文件API - 对应 /upload 接口"""

    def __init__(self):
        super().__init__()
        self._host = "http://localhost:8003"

    def set_host(self, host: str):
        """设置API服务器地址"""
        self._host = host.rstrip('/')

    def _get_url(self, path: str) -> str:
        """获取完整URL"""
        return urljoin(self._host + "/", path)

    def upload_file(self, data: ApiDataModel) -> ApiDataModel:
        """
        文件上传接口
        POST /upload
        @param data: ApiDataModel
        @return: ApiDataModel
        """
        data.request.url = self._get_url("upload")
        if "Content-Type" in data.request.headers:
            del data.request.headers["Content-Type"]
        return self.http(data)

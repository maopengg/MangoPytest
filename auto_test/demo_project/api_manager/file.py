# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 文件API - 使用 Core APIClient
# @Time   : 2026-01-18 13:57
# @Author : 毛鹏

from auto_test.demo_project.core.api.client import APIClient


class FileAPI:
    """文件API - 对应 /upload 接口"""

    def __init__(self):
        self._client = APIClient(base_url="http://localhost:8003")

    def set_host(self, host: str):
        """设置API服务器地址"""
        self._client.set_base_url(host)

    def set_token(self, token: str):
        """设置认证token"""
        self._client.set_auth_token(token)

    def upload_file(self, file_path: str) -> dict:
        """
        文件上传接口
        POST /upload
        @param file_path: 文件路径
        @return: 响应字典
        """
        # 文件上传使用原生 requests，因为 APIClient 主要处理 JSON
        import requests
        url = f"{self._client.base_url}/upload"
        headers = {}
        if self._client.auth_token:
            headers["Authorization"] = f"Bearer {self._client.auth_token}"

        with open(file_path, "rb") as f:
            files = {"file": f}
            response = requests.post(url, files=files, headers=headers)
        return response.json()

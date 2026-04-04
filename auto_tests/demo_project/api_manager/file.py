# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 文件API - 使用 Core APIClient
# @Time   : 2026-01-18 13:57
# @Author : 毛鹏

from core.base import BaseAPI


class FileAPI(BaseAPI):
    """文件API - 对应 /upload 接口"""

    def upload_file(self, file_path: str, headers: dict = None) -> dict:
        """
        文件上传接口
        POST /upload
        @param file_path: 文件路径
        @param headers: 请求头
        @return: 响应字典
        """
        response = self.client.upload("/upload", file_path, headers=headers)
        return response.data

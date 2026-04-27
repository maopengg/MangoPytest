# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 文件管理API - 不依赖Excel装饰器
# @Time   : 2026-01-18 13:57
# @Author : 毛鹏

from typing import Dict, Any, Optional

from core.api.client import APIClient


class FileAPI:
    """文件管理API类 - 直接调用API，不依赖Excel"""

    def __init__(self, base_url: str = "http://43.142.161.61:8003", headers: Dict = None):
        self.client = APIClient(base_url=base_url)
        if headers:
            self.client.headers = headers

    def upload_file(self, file_path: str, folder: Optional[str] = None) -> Dict[str, Any]:
        """
        文件上传接口
        @param file_path: 本地文件路径
        @param folder: 目标文件夹
        @return: 响应数据字典
        """
        response = self.client.upload("/upload", file_path=file_path, data={"folder": folder} if folder else None)
        return response.data

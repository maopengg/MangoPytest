# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 系统管理API - 不依赖Excel装饰器
# @Time   : 2026-01-18 13:58
# @Author : 毛鹏

from typing import Dict, Any, Optional

from core.api.client import APIClient


class SystemAPI:
    """系统管理API类 - 直接调用API，不依赖Excel"""

    def __init__(self, base_url: str = "http://43.142.161.61:8003", headers: Dict = None):
        self.client = APIClient(base_url=base_url)
        if headers:
            self.client.headers = headers

    def health_check(self) -> Dict[str, Any]:
        """
        健康检查接口
        @return: 响应数据字典
        """
        response = self.client.get("/health")
        return response.data

    def get_server_info(self) -> Dict[str, Any]:
        """
        获取服务器信息接口
        @return: 响应数据字典
        """
        response = self.client.get("/info")
        return response.data

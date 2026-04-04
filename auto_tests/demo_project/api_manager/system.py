# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 系统API - 使用 Core APIClient
# @Time   : 2026-01-18 13:58
# @Author : 毛鹏

from core.base import BaseAPI


class SystemAPI(BaseAPI):
    """系统API - 对应 /health, /info 接口"""

    def health_check(self) -> dict:
        """
        健康检查接口
        GET /health
        @return: 响应字典
        """
        response = self.client.get("/health")
        return response.data

    def get_server_info(self) -> dict:
        """
        获取服务器信息接口
        GET /info
        @return: 响应字典
        """
        response = self.client.get("/info")
        return response.data

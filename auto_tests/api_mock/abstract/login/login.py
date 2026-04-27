# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 登录API - 不依赖Excel装饰器
# @Time   : 2024-03-17 19:50
# @Author : 毛鹏

from typing import Dict, Any

from core.api.client import APIClient


class LoginAPI:
    """登录API类 - 直接调用API，不依赖Excel"""

    def __init__(self, base_url: str = "http://43.142.161.61:8003"):
        self.client = APIClient(base_url=base_url)

    def api_login(self, username: str, password: str) -> Dict[str, Any]:
        """
        登录接口
        @param username: 用户名
        @param password: 密码（MD5格式）
        @return: 响应数据字典
        """
        response = self.client.post("/auth/login", json={
            "username": username,
            "password": password
        })
        return response.data

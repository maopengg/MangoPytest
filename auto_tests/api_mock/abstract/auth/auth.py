# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description:认证API - 不依赖Excel装饰器
# @Time   : 2026-01-18 13:55
# @Author : 毛鹏

import hashlib
from typing import Dict, Any

from auto_tests.api_mock import user_info
from core.api.client import APIClient


class AuthAPI:
    """认证API类 - 直接调用API，不依赖Excel"""

    def __init__(self, base_url: str = "http://43.142.161.61:8003"):
        self.client = APIClient(base_url=base_url)

    def api_login(self, username: str = None, password: str = None) -> Dict[str, Any]:
        """
        用户登录接口
        @param username: 用户名，默认使用user_info中的用户名
        @param password: 密码，默认使用user_info中的密码（已MD5）
        @return: 响应数据字典
        """
        if username is None:
            username = user_info["username"]
        if password is None:
            password = user_info["password"]

        response = self.client.post("/auth/login", json={
            "username": username,
            "password": password
        })
        return response.data

    def api_register(self, username: str, email: str, full_name: str, password: str) -> Dict[str, Any]:
        """
        用户注册接口
        @param username: 用户名
        @param email: 邮箱
        @param full_name: 全名
        @param password: 密码（明文，内部会转MD5）
        @return: 响应数据字典
        """
        password_md5 = hashlib.md5(password.encode()).hexdigest()

        response = self.client.post("/auth/register", json={
            "username": username,
            "email": email,
            "full_name": full_name,
            "password": password_md5
        })
        return response.data

    def get_token(self) -> str:
        """
        获取登录token
        @return: token字符串
        """
        response = self.api_login()
        if response.get("code") == 200:
            return response["data"]["token"]
        return None

    def get_auth_headers(self) -> Dict[str, str]:
        """
        获取认证headers
        @return: 包含token的headers字典
        """
        token = self.get_token()
        if token:
            return {
                "X-Token": token,
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
        return {}

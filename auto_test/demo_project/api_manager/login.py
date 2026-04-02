# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 登录API - 使用 Core APIClient
# @Time   : 2024-03-17 19:50
# @Author : 毛鹏

import hashlib
from auto_test.demo_project.core.api.client import APIClient


class LoginAPI:
    """登录API - 对应 /auth/login 接口"""

    def __init__(self):
        self._client = APIClient(base_url="http://localhost:8003")

    def set_host(self, host: str):
        """设置API服务器地址"""
        self._client.set_base_url(host)

    def _encrypt_password(self, password: str) -> str:
        """对密码进行 MD5 加密"""
        return hashlib.md5(password.encode()).hexdigest()

    def api_login(self, username: str, password: str) -> dict:
        """
        登录接口
        POST /auth/login
        @param username: 用户名
        @param password: 密码（明文，会自动加密）
        @return: 响应字典
        """
        # 对密码进行 MD5 加密
        password_md5 = self._encrypt_password(password)
        response = self._client.post(
            "/auth/login",
            data={"username": username, "password": password_md5}
        )
        return response.data

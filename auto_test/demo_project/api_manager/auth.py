# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 认证API - 使用 Core APIClient
# @Time   : 2026-01-18 13:55
# @Author : 毛鹏

import hashlib

from auto_test.demo_project.core.api.client import APIClient


class AuthAPI:
    """认证API - 对应 /auth/login, /auth/register"""

    def __init__(self):
        self._client = APIClient(base_url="http://localhost:8003")

    def set_host(self, host: str):
        """设置API服务器地址"""
        self._client.set_base_url(host)

    def set_token(self, token: str):
        """设置认证token"""
        self._client.set_auth_token(token)

    def _encrypt_password(self, password: str) -> str:
        """对密码进行 MD5 加密"""
        return hashlib.md5(password.encode()).hexdigest()

    def api_login(self, username: str, password: str) -> dict:
        """
        用户登录接口
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

    def api_register(
            self, username: str, email: str, full_name: str, password: str
    ) -> dict:
        """
        用户注册接口
        POST /auth/register
        @param username: 用户名
        @param email: 邮箱
        @param full_name: 全名
        @param password: 密码（明文，会自动加密）
        @return: 响应字典
        """
        # 对密码进行 MD5 加密
        password_md5 = self._encrypt_password(password)
        response = self._client.post(
            "/auth/register",
            data={
                "username": username,
                "email": email,
                "full_name": full_name,
                "password": password_md5,
            }
        )
        return response.data

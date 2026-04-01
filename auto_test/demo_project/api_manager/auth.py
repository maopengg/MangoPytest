# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description:
# @Time   : 2026-01-18 13:55
# @Author : 毛鹏
from urllib.parse import urljoin

import requests


class AuthAPI:
    """认证API - 对应 /auth/login, /auth/register"""

    def __init__(self):
        self._host = "http://localhost:8003"

    def set_host(self, host: str):
        """设置API服务器地址"""
        self._host = host.rstrip("/")

    def _get_url(self, path: str) -> str:
        """获取完整URL"""
        return urljoin(self._host + "/", path)

    def api_login(self, username: str, password: str) -> dict:
        """
        用户登录接口
        POST /auth/login
        @param username: 用户名
        @param password: 密码
        @return: 响应字典
        """
        url = self._get_url("auth/login")
        response = requests.post(url, json={"username": username, "password": password})
        return response.json()

    def api_register(
        self, username: str, email: str, full_name: str, password: str
    ) -> dict:
        """
        用户注册接口
        POST /auth/register
        @param username: 用户名
        @param email: 邮箱
        @param full_name: 全名
        @param password: 密码
        @return: 响应字典
        """
        url = self._get_url("auth/register")
        response = requests.post(
            url,
            json={
                "username": username,
                "email": email,
                "full_name": full_name,
                "password": password,
            },
        )
        return response.json()

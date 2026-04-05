# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 认证API - 使用 Core APIClient
# @Time   : 2026-01-18 13:55
# @Author : 毛鹏

import hashlib

from ..base import DemoProjectBaseAPI


class AuthAPI(DemoProjectBaseAPI):
    """认证API - 对应 /auth/login, /auth/register"""

    def api_login(self, username: str, password: str) -> dict:
        """
        用户登录接口
        POST /auth/login
        @param username: 用户名
        @param password: 密码（明文，会自动加密）
        @return: 响应字典
        """
        password_md5 = hashlib.md5(password.encode()).hexdigest()
        response = self.client.post(
            "/auth/login", json={"username": username, "password": password_md5}
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
        password_md5 = hashlib.md5(password.encode()).hexdigest()
        response = self.client.post(
            "/auth/register",
            json={
                "username": username,
                "email": email,
                "full_name": full_name,
                "password": password_md5,
            },
        )
        return response.data

# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description:
# @Time   : 2024-03-17 19:50
# @Author : 毛鹏
from urllib.parse import urljoin

import requests


class UserAPI:
    """用户API - 对应 /users 接口"""

    def __init__(self):
        self._host = "http://localhost:8003"
        self._token = None

    def set_host(self, host: str):
        """设置API服务器地址"""
        self._host = host.rstrip("/")

    def set_token(self, token: str):
        """设置认证token"""
        self._token = token

    def _get_url(self, path: str) -> str:
        """获取完整URL"""
        return urljoin(self._host + "/", path)

    def _get_headers(self) -> dict:
        """获取请求头"""
        headers = {}
        if self._token:
            headers["X-Token"] = self._token
        return headers

    def get_users(self) -> dict:
        """
        获取用户列表
        GET /users
        @return: 响应字典
        """
        url = self._get_url("users")
        response = requests.get(url, headers=self._get_headers())
        return response.json()

    def get_user_by_id(self, user_id: int) -> dict:
        """
        根据ID获取用户
        GET /users?id={user_id}
        @param user_id: 用户ID
        @return: 响应字典
        """
        url = self._get_url("users")
        response = requests.get(
            url, params={"id": user_id}, headers=self._get_headers()
        )
        return response.json()

    def create_user(
        self, username: str, email: str, full_name: str, password: str
    ) -> dict:
        """
        创建用户
        POST /users
        @param username: 用户名
        @param email: 邮箱
        @param full_name: 全名
        @param password: 密码
        @return: 响应字典
        """
        url = self._get_url("users")
        response = requests.post(
            url,
            json={
                "username": username,
                "email": email,
                "full_name": full_name,
                "password": password,
            },
            headers=self._get_headers(),
        )
        return response.json()

    def update_user(self, user_id: int, **kwargs) -> dict:
        """
        更新用户
        PUT /users?user_id={user_id}
        @param user_id: 用户ID
        @param kwargs: 更新字段
        @return: 响应字典
        """
        url = self._get_url("users")
        response = requests.put(
            url, params={"user_id": user_id}, json=kwargs, headers=self._get_headers()
        )
        return response.json()

    def delete_user(self, user_id: int) -> dict:
        """
        删除用户
        DELETE /users?id={user_id}
        @param user_id: 用户ID
        @return: 响应字典
        """
        url = self._get_url("users")
        response = requests.delete(
            url, params={"id": user_id}, headers=self._get_headers()
        )
        return response.json()

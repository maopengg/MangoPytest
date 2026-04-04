# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 用户API - 使用 Core APIClient
# @Time   : 2024-03-17 19:50
# @Author : 毛鹏

import hashlib

from core.api.client import APIClient


class UserAPI:
    """用户API - 对应 /users 接口"""

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

    def get_users(self) -> dict:
        """
        获取用户列表
        GET /users
        @return: 响应字典
        """
        response = self._client.get("/users")
        return response.data

    def get_user_by_id(self, user_id: int) -> dict:
        """
        根据ID获取用户
        GET /users?id={user_id}
        @param user_id: 用户ID
        @return: 响应字典
        """
        response = self._client.get("/users", params={"id": user_id})
        return response.data

    def create_user(
            self, username: str, email: str, full_name: str, password: str
    ) -> dict:
        """
        创建用户
        POST /users
        @param username: 用户名
        @param email: 邮箱
        @param full_name: 全名
        @param password: 密码（明文，会自动加密）
        @return: 响应字典
        """
        # 对密码进行 MD5 加密
        password_md5 = self._encrypt_password(password)
        response = self._client.post(
            "/users",
            data={
                "username": username,
                "email": email,
                "full_name": full_name,
                "password": password_md5,
            }
        )
        return response.data

    def update_user(self, user_id: int, **kwargs) -> dict:
        """
        更新用户
        PUT /users/{user_id}
        @param user_id: 用户ID
        @param kwargs: 更新字段
        @return: 响应字典
        """
        response = self._client.put(
            f"/users/{user_id}",
            data=kwargs
        )
        return response.data

    def delete_user(self, user_id: int) -> dict:
        """
        删除用户
        DELETE /users/{user_id}
        @param user_id: 用户ID
        @return: 响应字典
        """
        response = self._client.delete(f"/users/{user_id}")
        return response.data

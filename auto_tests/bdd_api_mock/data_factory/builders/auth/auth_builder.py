# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 认证构造器 - 对应 /auth/login, /auth/register
# @Time   : 2026-03-31
# @Author : 毛鹏
import uuid
from typing import Dict, Any, Optional

from auto_tests.bdd_api_mock.api_manager import bdd_api_mock
from ...registry import register_builder


@register_builder("auth")
class AuthBuilder:
    """
    认证构造器
    对应 /auth/login, /auth/register 接口
    """

    def __init__(self, token: str = None, factory=None):
        self.token = token
        self.factory = factory
        self.default_username = "testuser"
        self.default_password = "password123"  # 明文密码，发送前会进行 MD5 加密

    def build_login_data(
            self, username: str = None, password: str = None
    ) -> Dict[str, Any]:
        """
        构造登录数据（不调用API）
        @return: 登录数据字典
        """
        return {
            "username": username or self.default_username,
            "password": password or self.default_password,
        }

    def build_register_data(
            self,
            username: str = None,
            email: str = None,
            full_name: str = None,
            password: str = None,
            role: str = None,
    ) -> Dict[str, Any]:
        """
        构造注册数据（不调用API）
        @return: 注册数据字典
        """
        return {
            "username": username or f"user_{uuid.uuid4().hex[:8]}",
            "email": email or f"{uuid.uuid4().hex[:8]}@example.com",
            "full_name": full_name or f"Test User {uuid.uuid4().hex[:4]}",
            "password": password or "123456",
            "role": role or "user",
        }

    def login(self, username: str = None, password: str = None) -> Optional[str]:
        """
        用户登录
        @return: token
        """
        login_data = self.build_login_data(username, password)

        # 直接传递明文密码，由 API 层进行加密
        result = bdd_api_mock.auth.api_login(
            username=login_data["username"], password=login_data["password"]
        )

        if result.get("code") == 200:
            token = result["data"]["token"]
            self.token = token
            return token

        return None

    def register(
            self,
            username: str = None,
            email: str = None,
            full_name: str = None,
            password: str = None,
            role: str = None,
    ) -> Dict[str, Any]:
        """
        用户注册
        @param username: 用户名
        @param email: 邮箱
        @param full_name: 全名
        @param password: 密码
        @param role: 角色（注：API可能不支持，仅用于返回数据）
        @return: 创建的用户数据
        """
        register_data = self.build_register_data(username, email, full_name, password, role)

        # 直接传递明文密码，由 API 层进行加密
        result = bdd_api_mock.auth.api_register(
            username=register_data["username"],
            email=register_data["email"],
            full_name=register_data["full_name"],
            password=register_data["password"],
        )
        if result.get("code") == 200:
            data = result["data"]
            # 如果指定了 role 但 API 返回的数据中没有，则添加它
            if role and "role" not in data:
                data["role"] = role
            return data
        return {}

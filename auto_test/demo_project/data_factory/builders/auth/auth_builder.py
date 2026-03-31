# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 认证构造器 - 对应 /auth/login, /auth/register
# @Time   : 2026-03-31
# @Author : 毛鹏
from typing import Dict, Any, Optional
import uuid
import hashlib

from ..base_builder import BaseBuilder
from auto_test.demo_project.api_manager import demo_project
from ...registry import register_builder


@register_builder("auth")
class AuthBuilder(BaseBuilder):
    """
    认证构造器
    对应 /auth/login, /auth/register 接口
    """

    def __init__(self, token: str = None, factory=None):
        super().__init__(token, factory)
        self.default_username = "testuser"
        self.default_password = "482c811da5d5b4bc6d497ffa98491e38"

    def build_login_data(self, username: str = None, password: str = None) -> Dict[str, Any]:
        """
        构造登录数据（不调用API）
        @return: 登录数据字典
        """
        return {
            "username": username or self.default_username,
            "password": password or self.default_password
        }

    def build_register_data(self, username: str = None, email: str = None,
                           full_name: str = None, password: str = None) -> Dict[str, Any]:
        """
        构造注册数据（不调用API）
        @return: 注册数据字典
        """
        return {
            "username": username or f"user_{uuid.uuid4().hex[:8]}",
            "email": email or f"{uuid.uuid4().hex[:8]}@example.com",
            "full_name": full_name or f"Test User {uuid.uuid4().hex[:4]}",
            "password": password or "123456"
        }

    def login(self, username: str = None, password: str = None) -> Optional[str]:
        """
        用户登录
        @return: token
        """
        login_data = self.build_login_data(username, password)

        api_data = self._create_api_data(
            url="/auth/login",
            method="POST",
            json_data=login_data
        )

        result = demo_project.auth.api_login(api_data)
        if result.response and result.response.json().get("code") == 200:
            token = result.response.json()["data"]["token"]
            self.token = token
            return token
        return None

    def register(self, username: str = None, email: str = None,
                 full_name: str = None, password: str = None) -> Dict[str, Any]:
        """
        用户注册
        @return: 创建的用户数据
        """
        register_data = self.build_register_data(username, email, full_name, password)

        api_data = self._create_api_data(
            url="/auth/register",
            method="POST",
            json_data=register_data
        )

        result = demo_project.auth.api_register(api_data)
        if result.response and result.response.json().get("code") == 200:
            created_user = result.response.json()["data"]
            self._register_created(created_user)
            return created_user
        return None

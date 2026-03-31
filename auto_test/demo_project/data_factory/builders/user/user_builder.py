# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 用户构造器 - 对应 /users 接口
# @Time   : 2026-03-31
# @Author : 毛鹏
from typing import Dict, Any, List, Optional
import uuid
import hashlib

from ..base_builder import BaseBuilder
from auto_test.demo_project.api_manager import demo_project
from ...registry import register_builder


@register_builder("user")
class UserBuilder(BaseBuilder):
    """
    用户构造器
    对应 /users 接口 (GET, PUT, DELETE)
    """

    def __init__(self, token: str = None, factory=None):
        super().__init__(token, factory)

    def build(self, username: str = None, email: str = None,
              full_name: str = None, password: str = None) -> Dict[str, Any]:
        """
        构造用户数据（不调用API）
        @return: 用户数据字典
        """
        return {
            "username": username or f"user_{uuid.uuid4().hex[:8]}",
            "email": email or f"{uuid.uuid4().hex[:8]}@example.com",
            "full_name": full_name or f"Test User {uuid.uuid4().hex[:4]}",
            "password": password or hashlib.md5("123456".encode()).hexdigest()
        }

    def get_all(self) -> List[Dict[str, Any]]:
        """
        获取所有用户
        @return: 用户列表
        """
        api_data = self._create_api_data(
            url="/users",
            method="GET"
        )

        result = demo_project.user.get_all_users(api_data)
        if result.response and result.response.json().get("code") == 200:
            return result.response.json()["data"]
        return []

    def get_by_id(self, user_id: int) -> Dict[str, Any]:
        """
        根据ID获取用户
        @param user_id: 用户ID
        @return: 用户数据
        """
        api_data = self._create_api_data(
            url="/users",
            method="GET",
            params={"id": user_id}
        )

        result = demo_project.user.get_user_by_id(api_data)
        if result.response and result.response.json().get("code") == 200:
            return result.response.json()["data"]
        return None

    def update(self, user_id: int, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新用户信息
        @param user_id: 用户ID
        @param user_data: 用户数据
        @return: 更新后的用户数据
        """
        api_data = self._create_api_data(
            url="/users",
            method="PUT",
            params={"id": user_id},
            json_data=user_data
        )

        result = demo_project.user.update_user_info(api_data)
        if result.response and result.response.json().get("code") == 200:
            return result.response.json()["data"]
        return None

    def delete(self, user_id: int) -> bool:
        """
        删除用户
        @param user_id: 用户ID
        @return: 是否删除成功
        """
        api_data = self._create_api_data(
            url="/users",
            method="DELETE",
            params={"id": user_id}
        )

        result = demo_project.user.delete_user(api_data)
        if result.response and result.response.json().get("code") == 200:
            return True
        return False

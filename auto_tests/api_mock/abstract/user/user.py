# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 用户管理API - 不依赖Excel装饰器
# @Time   : 2026-01-18 13:56
# @Author : 毛鹏

from typing import Dict, Any, Optional

from core.api.client import APIClient


class UserAPI:
    """用户管理API类 - 直接调用API，不依赖Excel"""

    def __init__(self, base_url: str = "http://43.142.161.61:8003", headers: Dict = None):
        self.client = APIClient(base_url=base_url)
        if headers:
            self.client.headers = headers

    def get_all_users(self) -> Dict[str, Any]:
        """
        获取所有用户接口
        @return: 响应数据字典
        """
        response = self.client.get("/users")
        return response.data

    def get_user_by_id(self, user_id: int) -> Dict[str, Any]:
        """
        根据ID获取用户接口
        @param user_id: 用户ID
        @return: 响应数据字典
        """
        response = self.client.get("/users", params={"id": user_id})
        return response.data

    def update_user_info(self, user_id: int, username: str, email: str, 
                         full_name: str, role: str, password: str) -> Dict[str, Any]:
        """
        更新用户信息接口
        @param user_id: 用户ID
        @param username: 用户名
        @param email: 邮箱
        @param full_name: 全名
        @param role: 角色
        @param password: 密码
        @return: 响应数据字典
        """
        update_data = {
            "username": username,
            "email": email,
            "full_name": full_name,
            "role": role,
            "password": password
        }
        response = self.client.put(f"/users/{user_id}", json=update_data)
        return response.data

    def delete_user(self, user_id: int) -> Dict[str, Any]:
        """
        删除用户接口
        @param user_id: 用户ID
        @return: 响应数据字典
        """
        response = self.client.delete(f"/users/{user_id}")
        return response.data

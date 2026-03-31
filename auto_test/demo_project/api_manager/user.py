# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2026-01-18 13:56
# @Author : 毛鹏
from urllib.parse import urljoin

from models.api_model import ApiDataModel
from tools.base_request.request_tool import RequestTool
from tools.decorator.response import request_data


class UserAPI(RequestTool):
    """用户API - 对应 /users 接口"""

    def __init__(self):
        super().__init__()
        self._host = "http://localhost:8003"

    def set_host(self, host: str):
        """设置API服务器地址"""
        self._host = host.rstrip('/')

    def _get_url(self, path: str) -> str:
        """获取完整URL"""
        return urljoin(self._host + "/", path)

    def get_all_users(self, data: ApiDataModel) -> ApiDataModel:
        """
        获取所有用户接口
        GET /users
        @param data: ApiDataModel
        @return: ApiDataModel
        """
        data.request.url = self._get_url("users")
        return self.http(data)

    def get_user_by_id(self, data: ApiDataModel) -> ApiDataModel:
        """
        根据ID获取用户接口
        GET /users?id={id}
        @param data: ApiDataModel
        @return: ApiDataModel
        """
        data.request.url = self._get_url("users")
        return self.http(data)

    def update_user_info(self, data: ApiDataModel) -> ApiDataModel:
        """
        更新用户信息接口
        PUT /users?id={id}
        @param data: ApiDataModel
        @return: ApiDataModel
        """
        data.request.url = self._get_url("users")
        return self.http(data)

    def delete_user(self, data: ApiDataModel) -> ApiDataModel:
        """
        删除用户接口
        DELETE /users?id={id}
        @param data: ApiDataModel
        @return: ApiDataModel
        """
        data.request.url = self._get_url("users")
        return self.http(data)

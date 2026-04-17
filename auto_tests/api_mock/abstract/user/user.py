# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2026-01-18 13:56
# @Author : 毛鹏

from auto_tests.api_mock import base_data
from core.models.api_model import ApiDataModel
from core.api.request_tool import RequestTool
from core.decorators import request_data


class UserAPI(RequestTool):
    base_data = base_data

    @request_data(3)
    def get_all_users(self, data: ApiDataModel) -> ApiDataModel:
        """
        获取所有用户接口
        @param data: ApiDataModel
        @return: ApiDataModel
        """
        return self.http(data)

    @request_data(4)
    def get_user_by_id(self, data: ApiDataModel) -> ApiDataModel:
        """
        根据ID获取用户接口
        @param data: ApiDataModel
        @return: ApiDataModel
        """
        return self.http(data)

    @request_data(5)
    def update_user_info(self, data: ApiDataModel) -> ApiDataModel:
        """
        更新用户信息接口
        @param data: ApiDataModel
        @return: ApiDataModel
        """
        return self.http(data)

    @request_data(6)
    def delete_user(self, data: ApiDataModel) -> ApiDataModel:
        """
        删除用户接口
        @param data: ApiDataModel
        @return: ApiDataModel
        """
        return self.http(data)

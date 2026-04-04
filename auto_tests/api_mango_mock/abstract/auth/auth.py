# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2026-01-18 13:55
# @Author : 毛鹏

from auto_tests.api_mango_mock import base_data
from core.models.api_model import ApiDataModel
from tools.base_request.request_tool import RequestTool
from tools.decorator.response import request_data


class AuthAPI(RequestTool):
    base_data = base_data

    @request_data(1)
    def api_login(self, data: ApiDataModel) -> ApiDataModel:
        """
        用户登录接口
        @param data: ApiDataModel
        @return: ApiDataModel
        """
        return self.http(data)

    @request_data(2)
    def api_register(self, data: ApiDataModel) -> ApiDataModel:
        """
        用户注册接口
        @param data: ApiDataModel
        @return: ApiDataModel
        """
        return self.http(data)

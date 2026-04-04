# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-03-17 19:50
# @Author : 毛鹏
from auto_tests.api_mango_mock import base_data
from core.models.api_model import ApiDataModel
from core.api.request_tool import RequestTool
from core.decorators import request_data


class LoginAPI(RequestTool):
    base_data = base_data

    @request_data(1)
    def api_login(self, data: ApiDataModel) -> ApiDataModel:
        """
        登录接口
        @param data: ApiDataModel
        @return: ApiDataModel
        """
        return self.http(data)

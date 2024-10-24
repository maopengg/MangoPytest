# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-03-17 19:50
# @Author : 毛鹏
from auto_test.api.wan_android import WanAndroidDataModel
from models.api_model import ApiDataModel
from tools.base_request.request_tool import RequestTool
from tools.decorator.response import request_data


class LoginAPI(RequestTool):
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data_model = WanAndroidDataModel()

    @request_data
    def api_login(self, data: ApiDataModel) -> ApiDataModel:
        """
        登录接口
        @param data: ApiDataModel
        @return: ApiDataModel
        """
        return self.http(data)

    def api_reset_password(self) -> ApiDataModel:
        pass

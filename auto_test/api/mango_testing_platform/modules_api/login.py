# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-03-17 19:50
# @Author : 毛鹏
from auto_test.api.mango_testing_platform import MangoDataModel
from models.api_model import ApiDataModel
from tools.base_request.request_tool import RequestTool
from tools.decorator.response import request_data


class LoginAPI(RequestTool):
    data_model = MangoDataModel()

    @request_data(3)
    def api_login(self, data: ApiDataModel) -> ApiDataModel:
        """
        登录接口
        @param data: ApiDataModel
        @return: ApiDataModel
        """
        data.request.headers = {}
        return self.http(data)

    def api_reset_password(self) -> ApiDataModel:
        pass

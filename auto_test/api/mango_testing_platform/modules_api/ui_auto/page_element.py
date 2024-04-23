# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2024-04-23 11:19
# @Author : 毛鹏
from auto_test.api.mango_testing_platform import MangoDataModel
from models.api_model import ApiDataModel
from tools.base_request.request_tool import RequestTool
from tools.decorator.response import request_data


class PageElementAPI(RequestTool):
    data_model = MangoDataModel()

    @request_data(4)
    def page_element_list(self, data: ApiDataModel) -> ApiDataModel:
        """
        登录接口
        @param data: ApiDataModel
        @return: ApiDataModel
        """
        return self.http(data)

    def api_reset_password(self) -> ApiDataModel:
        pass

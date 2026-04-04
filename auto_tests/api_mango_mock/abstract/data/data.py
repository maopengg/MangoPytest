# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2026-01-18 13:57
# @Author : 毛鹏

from auto_tests.api_mango_mock import base_data
from models.api_model import ApiDataModel
from tools.base_request.request_tool import RequestTool
from tools.decorator.response import request_data


class DataAPI(RequestTool):
    base_data = base_data

    @request_data(18)
    def submit_data(self, data: ApiDataModel) -> ApiDataModel:
        """
        提交数据接口
        @param data: ApiDataModel
        @return: ApiDataModel
        """
        return self.http(data)

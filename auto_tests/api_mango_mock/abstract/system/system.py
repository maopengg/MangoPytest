# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2026-01-18 13:58
# @Author : 毛鹏

from auto_test.api_mango_mock import base_data
from models.api_model import ApiDataModel
from tools.base_request.request_tool import RequestTool
from tools.decorator.response import request_data


class SystemAPI(RequestTool):
    base_data = base_data

    @request_data(19)
    def health_check(self, data: ApiDataModel) -> ApiDataModel:
        """
        健康检查接口
        @param data: ApiDataModel
        @return: ApiDataModel
        """
        return self.http(data)

    @request_data(20)
    def get_server_info(self, data: ApiDataModel) -> ApiDataModel:
        """
        获取服务器信息接口
        @param data: ApiDataModel
        @return: ApiDataModel
        """
        return self.http(data)

# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-12-05 11:53
# @Author : 毛鹏

from models.api_model import ApiDataModel
from models.models import AigcSaasDataModel
from tools.data_processor import DataProcessor
from tools.decorator.response import around
from tools.request_tool.request_tool import RequestTool


class LoginApi(DataProcessor, RequestTool):
    data_model: AigcSaasDataModel = AigcSaasDataModel()

    @classmethod
    @around(41)
    def login(cls, data: ApiDataModel) -> ApiDataModel:
        """
        登录接口
        @param data:
        @return:
        """
        response: ApiDataModel = cls.http(data)
        return response

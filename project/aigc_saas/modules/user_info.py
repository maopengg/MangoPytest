# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-12-08 15:13
# @Author : 毛鹏
from models.api_model import ApiDataModel
from models.models import AigcSaasDataModel
from tools.data_processor import DataProcessor
from tools.decorator.response import around
from tools.request_tool.request_tool import RequestTool


class UserInfoApi(DataProcessor, RequestTool):
    data_model: AigcSaasDataModel = AigcSaasDataModel()

    @classmethod
    @around(42)
    def get_user_info(cls, data: ApiDataModel) -> ApiDataModel:
        response: ApiDataModel = cls.http(data)
        return response

    @classmethod
    @around(44)
    def get_routers(cls, data: ApiDataModel) -> ApiDataModel:
        response: ApiDataModel = cls.http(data)
        return response

    @classmethod
    @around(43)
    def get_enterprise_info(cls, data: ApiDataModel) -> ApiDataModel:
        response: ApiDataModel = cls.http(data)
        return response

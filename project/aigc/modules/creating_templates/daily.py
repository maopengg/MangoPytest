# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-08-08 11:25
# @Author : 毛鹏
from requests.models import Response

from models.api_model import ApiInfoModel
from project.aigc import AIGCDataModel
from tools.data_processor import DataProcessor
from tools.decorator.response import around
from tools.request_tool.request_tool import RequestTool


class CreatingTemplatesAPI(DataProcessor, RequestTool):
    data_model: AIGCDataModel = AIGCDataModel()

    @classmethod
    @around(3)
    def api_daily_list(cls, api_info: ApiInfoModel = None) -> tuple[Response, str, dict] | Response:
        """
        小红书每日报告list
        :return: 响应结果，请求url，请求头
        """
        url = f'{cls.data_model.host}{api_info.url}{cls.data_model.username}'
        response = cls.http_get(url=url, headers=cls.data_model.headers)
        return response, url, cls.data_model.headers


if __name__ == '__main__':
    pass

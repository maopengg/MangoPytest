# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 小红书笔记
# @Time   : 2023-09-01 14:55
# @Author : 毛鹏

from models.api_model import ApiDataModel
from models.models import AIGCDataModel
from tools.data_processor import DataProcessor
from tools.decorator.response import around
from tools.request_tool.request_tool import RequestTool


class NoteAPI(DataProcessor, RequestTool):
    """ 小红书笔记 """
    data_model: AIGCDataModel = AIGCDataModel()

    @classmethod
    @around(4)
    def api_note_dress(cls, data: ApiDataModel) -> ApiDataModel:
        """
        小红书笔记
        :return:
        """
        return cls.http(data)

    @classmethod
    @around(5)
    def api_note_dress_title(cls, data: ApiDataModel) -> ApiDataModel:
        """
        生成小红书标题
        :return:
        """
        return cls.http(data)

    @classmethod
    @around(6)
    def api_note_article(cls, data: ApiDataModel) -> ApiDataModel:
        """
        小红书笔记
        :return:
        """
        return cls.http(data)

    @classmethod
    @around(26)
    def api_get_note_filter_dropdown_options(cls, data: ApiDataModel) -> ApiDataModel:
        """
        小红书笔记
        :return:
        """
        return cls.http(data)

    @classmethod
    @around(29)
    def api_note_add_keyword(cls, data: ApiDataModel) -> ApiDataModel:
        return cls.http(data)

    @classmethod
    @around(31)
    def api_note_query_classification(cls, data: ApiDataModel) -> ApiDataModel:
        return cls.http(data)

    @classmethod
    @around(40)
    def api_note_stop(cls, data: ApiDataModel) -> ApiDataModel:
        return cls.http(data)


if __name__ == '__main__':
    import requests

    url = "https://aigc-test.growknows.cn/api/note/getKeyword?id=2"

    payload = {}
    headers = {
        'Authorization': 'Bearer ad0e3d81b2dd4ea1be338d354f0ed9e2',
        'User': 'auto_aigc',
        'Userid': '121'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    print(response.text)

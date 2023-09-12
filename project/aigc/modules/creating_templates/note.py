# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-09-01 14:55
# @Author : 毛鹏
from requests.models import Response

from models.api_model import ApiInfoModel
from project.aigc import AIGCDataModel
from project.aigc.modules.creating_templates.model import NoteRequestModel
from tools.data_processor import DataProcessor
from tools.decorator.response import around
from tools.request_tool.request_tool import RequestTool


class NoteAPI(DataProcessor, RequestTool):
    """ 小红书笔记 """
    data_model: AIGCDataModel = AIGCDataModel()

    @classmethod
    @around(4)
    def api_note_dress(cls, _type, api_info: ApiInfoModel = None) -> tuple[Response, str, dict] | Response:
        """
        小红书笔记
        :return:
        """
        url = f'{cls.data_model.host}{api_info.url}{_type}'
        response = cls.http_get(url=url, headers=cls.data_model.headers)
        return response, url, cls.data_model.headers

    @classmethod
    @around(5)
    def api_note_dress_title(cls, note_data: NoteRequestModel, api_info: ApiInfoModel = None) -> tuple[
                                                                                                     Response, str, dict] | Response:
        """
        生成小红书标题
        :param note_data:
        :return:
        """
        url = f'{cls.data_model.host}{api_info.url}'
        response = cls.http_post(url, headers=cls.data_model.headers, json=note_data.dict())
        return response, url, cls.data_model.headers

    @classmethod
    @around(6)
    def api_note_article(cls, note_data: NoteRequestModel, api_info: ApiInfoModel = None) -> tuple[
                                                                                                 Response, str, dict] | Response:
        """
        小红书笔记
        :return:
        """
        url = f'{cls.data_model.host}{api_info.url}'
        response = cls.http_post(url, headers=cls.data_model.headers, json=note_data.dict())
        return response, url, cls.data_model.headers

    # @classmethod
    # @around('小红书笔记-配饰达人')
    # def api_note_accessories(cls) -> tuple[Response, str, dict] | Response:
    #     """
    #     小红书笔记
    #     :return:
    #     """
    #     url = f'{cls.data_model.host}api/note/getKeyword?id={3}'
    #     response = cls.http_get(url=url, headers=cls.data_model.headers)
    #     return response, url, cls.data_model.headers
    #
    # @classmethod
    # @around('小红书笔记-家具达人')
    # def api_note_furniture(cls) -> tuple[Response, str, dict] | Response:
    #     """
    #     小红书笔记
    #     :return:
    #     """
    #     url = f'{cls.data_model.host}api/note/getKeyword?id={7}'
    #     response = cls.http_get(url=url, headers=cls.data_model.headers)
    #     return response, url, cls.data_model.headers
    #
    # @classmethod
    # @around('小红书笔记-建材达人')
    # def api_note_building_materials(cls) -> tuple[Response, str, dict] | Response:
    #     """
    #     小红书笔记
    #     :return:
    #     """
    #     url = f'{cls.data_model.host}api/note/getKeyword?id={8}'
    #     response = cls.http_get(url=url, headers=cls.data_model.headers)
    #     return response, url, cls.data_model.headers


if __name__ == '__main__':
    theme_directionr = '选购攻略'
    plant = [
        {
            "id": 22,
            "name": "外套",
            "preset": 1,
            "children": None,
            "pid": 21
        },
        {
            "id": 30,
            "name": "背带裤",
            "preset": 1,
            "children": None,
            "pid": 29
        }
    ]
    target = [
        {
            "id": 110,
            "name": "打工族",
            "preset": 1,
            "children": None,
            "pid": 109
        }
    ]
    selling = [
        {
            "id": 122,
            "name": "显瘦",
            "preset": 1,
            "children": None,
            "pid": 121
        }
    ]
    keyword = [
        {
            "id": 179,
            "name": "春天",
            "preset": 1,
            "children": None,
            "pid": 178
        }
    ]
    response_data = NoteAPI.api_note_dress_title(theme_directionr, plant, target, selling,
                                                 keyword).json()
    data = response_data['data']
    decoded_data = data.encode('latin-1').decode('unicode_escape').encode('utf-8', 'ignore').decode('utf-8')
    print(decoded_data)

# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-08-08 11:25
# @Author : 毛鹏
import requests
from requests.models import Response

from project.aigc import AIGCDataModel
from tools.data_processor import DataProcessor
from tools.decorator.response import around


class CreatingTemplatesAPI(DataProcessor):
    data_model: AIGCDataModel = AIGCDataModel()

    @classmethod
    @around('小红书每日报告list')
    def api_daily_list(cls) -> tuple[Response, str, dict] | Response:
        """
        小红书每日报告list
        :return: 响应结果，请求url，请求头
        """
        url = f'{cls.data_model.host}api/brands/list?user={cls.data_model.username}'
        response = requests.get(url=url, headers=cls.data_model.headers)
        return response, url, cls.data_model.headers

    @classmethod
    @around('小红书笔记-服装达人')
    def api_note_dress(cls) -> tuple[Response, str, dict] | Response:
        """
        小红书笔记
        :return:
        """
        url = f'{cls.data_model.host}api/note/getKeyword?id={2}'
        response = requests.get(url=url, headers=cls.data_model.headers)
        return response, url, cls.data_model.headers

    @classmethod
    @around('小红书笔记-配饰达人')
    def api_note_accessories(cls) -> tuple[Response, str, dict] | Response:
        """
        小红书笔记
        :return:
        """
        url = f'{cls.data_model.host}api/note/getKeyword?id={3}'
        response = requests.get(url=url, headers=cls.data_model.headers)
        return response, url, cls.data_model.headers

    @classmethod
    @around('小红书笔记-家具达人')
    def api_note_furniture(cls) -> tuple[Response, str, dict] | Response:
        """
        小红书笔记
        :return:
        """
        url = f'{cls.data_model.host}api/note/getKeyword?id={7}'
        response = requests.get(url=url, headers=cls.data_model.headers)
        return response, url, cls.data_model.headers

    @classmethod
    @around('小红书笔记-建材达人')
    def api_note_building_materials(cls) -> tuple[Response, str, dict] | Response:
        """
        小红书笔记
        :return:
        """
        url = f'{cls.data_model.host}api/note/getKeyword?id={8}'
        response = requests.get(url=url, headers=cls.data_model.headers)
        return response, url, cls.data_model.headers


if __name__ == '__main__':
    print(CreatingTemplatesAPI.api_note_building_materials().json())

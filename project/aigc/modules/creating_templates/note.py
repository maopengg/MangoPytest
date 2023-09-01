# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-09-01 14:55
# @Author : 毛鹏
import requests
from requests.models import Response

from project.aigc import AIGCDataModel
from tools.data_processor import DataProcessor
from tools.decorator.response import around


class NoteAPI(DataProcessor):
    """ 小红书笔记 """
    data_model: AIGCDataModel = AIGCDataModel()

    @classmethod
    @around('服装达人-进入接口')
    def api_note_dress(cls, _type) -> tuple[Response, str, dict] | Response:
        """
        小红书笔记
        :return:
        """
        url = f'{cls.data_model.host}api/note/getKeyword?id={_type}'
        response = requests.get(url=url, headers=cls.data_model.headers)
        return response, url, cls.data_model.headers

    @classmethod
    @around('服装达人-生成小红书标题')
    def api_note_dress_title(cls, theme_direction: str, plant: list[dict], target: list[dict], selling: list[dict],
                             keyword: list[dict]) -> tuple[Response, str, dict] | Response:
        """
        生成小红书标题
        :param theme_direction:主体方向
        :param plant:种草产品
        :param target:目标人群
        :param selling:卖点效果
        :param keyword:其他关键词(季节、场景、材质、色系、风格等)
        :return:
        """

        url = f'{cls.data_model.host}api/ai/generateNotesTitle'
        json = {
            "first_type": "服饰配饰",
            "user": cls.data_model.headers.get('User'),
            "user_id": cls.data_model.headers.get('userId'),
            "second_type": "服饰",
            "theme_direction": theme_direction,
            "product_names": [obj.get('name') for obj in plant],
            "target_populations": [obj.get('name') for obj in target],
            "selling_points": [obj.get('name') for obj in selling],
            "other_keywords": [obj.get('name') for obj in keyword],
            "details": cls.json_dumps({"subject": theme_direction,
                                       "plant": plant,
                                       "target": target,
                                       "selling": selling,
                                       "keyword": keyword})
        }
        response = requests.post(url, headers=cls.data_model.headers, json=json)
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

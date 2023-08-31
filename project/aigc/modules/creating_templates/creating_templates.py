# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-08-08 11:25
# @Author : 毛鹏
import allure
import requests
from requests.models import Response

from project.aigc import AIGCDataModel
from tools.data_processor import DataProcessor
from tools.decorator.response import around
from tools.logging_tool.log_control import INFO


class CreatingTemplatesAPI(DataProcessor):
    data_model: AIGCDataModel = AIGCDataModel()

    @classmethod
    @around('小红书每日报告list')
    def api_daily_list(cls) -> Response:
        """
        小红书每日报告list
        :return:
        """
        api_name = '小红书每日报告list'
        url = f'{cls.data_model.host}api/brands/list?user={cls.data_model.username}'

        allure.attach(str(url), f'{api_name}->url')
        allure.attach(str(cls.data_model.headers), f'{api_name}-请求头')

        return requests.get(url=url, headers=cls.data_model.headers)

    @classmethod
    @around('小红书笔记-服装达人')
    def api_note_dress(cls) -> Response:
        """
        小红书笔记
        :return:
        """
        api_name = '小红书笔记-服装达人'
        url = f'{cls.data_model.host}api/note/getKeyword?id={2}'

        allure.attach(str(url), f'{api_name}->url')
        allure.attach(str(cls.data_model.headers), f'{api_name}->请求头')

        return requests.get(url=url, headers=cls.data_model.headers)

    @classmethod
    @around('小红书笔记-配饰达人')
    def api_note_accessories(cls) -> Response:
        """
        小红书笔记
        :return:
        """
        api_name = '小红书笔记-配饰达人'
        url = f'{cls.data_model.host}api/note/getKeyword?id={3}'

        allure.attach(str(url), f'{api_name}->url')
        allure.attach(str(cls.data_model.headers), f'{api_name}->请求头')

        return requests.get(url=url, headers=cls.data_model.headers)

    @classmethod
    @around('小红书笔记-家具达人')
    def api_note_furniture(cls) -> Response:
        """
        小红书笔记
        :return:
        """
        api_name = '小红书笔记-家具达人'
        url = f'{cls.data_model.host}api/note/getKeyword?id={7}'

        allure.attach(str(url), f'{api_name}->url')
        allure.attach(str(cls.data_model.headers), f'{api_name}->请求头')

        return requests.get(url=url, headers=cls.data_model.headers)

    @classmethod
    @around('小红书笔记-建材达人')
    def api_note_building_materials(cls) -> Response:
        """
        小红书笔记
        :return:
        """
        api_name = '小红书笔记-建材达人'
        url = f'{cls.data_model.host}api/note/getKeyword?id={8}'

        allure.attach(str(url), f'{api_name}->url')
        allure.attach(str(cls.data_model.headers), f'{api_name}->请求头')
        return requests.get(url=url, headers=cls.data_model.headers)


if __name__ == '__main__':
    print(CreatingTemplatesAPI.api_note_building_materials().json())

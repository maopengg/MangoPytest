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


class CreatingTemplatesAPI(DataProcessor):
    data_model: AIGCDataModel = AIGCDataModel()

    @classmethod
    @around()
    def api_daily_list(cls) -> Response:
        """
        小红书每日报告list
        :return:
        """
        api_name = "小红书每日报告list"
        url = f'{cls.data_model.host}api/brands/list?user={cls.data_model.username}'

        allure.attach(str(url), f'{api_name}-url')
        allure.attach(str(cls.data_model.headers), f'{api_name}-请求头')

        response = requests.get(url=url, headers=cls.data_model.headers)
        return response

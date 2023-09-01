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


class LoginAPI(DataProcessor):
    data_model: AIGCDataModel = AIGCDataModel()
    headers = {'Authorization': 'Bearer null',
               'Accept': 'application/json, text/plain, */*',
               'Content-Type': 'application/json;charset=UTF-8'}

    @classmethod
    @around('登录接口')
    def api_login(cls, username, password) -> tuple[Response, str, dict] | Response:
        """
        登录接口
        :return:
        """
        json = {'username': username, 'password': cls.md5_encrypt(password)}
        url = f'{cls.data_model.host}api/login'

        response = requests.post(url=url, headers=cls.headers, json=json)
        return response, url, cls.headers

    @classmethod
    @around('重置密码')
    def api_reset_password(cls) -> tuple[Response, str, dict] | Response:
        """
        重置密码
        :return:
        """

    @classmethod
    @around('退出登录')
    def api_login_out(cls, header: dict) -> tuple[Response, str, dict] | Response:
        """
        退出登录
        :return:
        """
        url = f'{cls.data_model.host}api/logout'

        response = requests.get(url=url, headers=header)
        return response, url, cls.headers


if __name__ == '__main__':
    r = LoginAPI.api_login('maopeng', 'maopeng').json()
    print(r)

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


class LoginAPI(DataProcessor):
    data_model: AIGCDataModel = AIGCDataModel()

    headers = {'Authorization': 'Bearer null',
               'Accept': 'application/json, text/plain, */*',
               'Content-Type': 'application/json;charset=UTF-8'}

    @classmethod
    @around('登录接口')
    def api_login(cls, username, password) -> Response:
        """
        登录接口
        :return:
        """
        password = cls.md5_encrypt(password)
        json = {"username": username, "password": password}
        url = cls.data_model.host + 'api/login'

        allure.attach(str(url), "请求url")
        allure.attach(str(cls.headers), "请求headers")

        response = requests.post(url=url, headers=cls.headers, json=json)
        return response

    @classmethod
    @around('重置密码')
    def api_reset_password(cls) -> Response:
        """
        重置密码
        :return:
        """

    @classmethod
    @around('退出登录')
    def api_login_out(cls, header: dict) -> Response:
        """
        退出登录
        :return:
        """
        url = cls.data_model.host + 'api/logout'

        allure.attach(str(url), "请求url")
        allure.attach(str(cls.json_dumps(header)), "请求headers")

        return requests.get(url=url, headers=header)


if __name__ == '__main__':
    r = LoginAPI.api_login('maopeng', 'maopeng').json()
    print(r)

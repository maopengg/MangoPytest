# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-08-08 11:25
# @Author : 毛鹏
import allure
import requests
from requests.models import Response
from enums.tools_enum import ProjectEnum
from tools.data_processor import DataProcessor
from tools.decorator.response import around


class LoginAPI(DataProcessor):
    project = ProjectEnum.AIGC.value
    headers = {
        'Authorization': 'Bearer null',
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json;charset=UTF-8',
    }

    @classmethod
    @around()
    def api_login(cls, username, password) -> Response:
        """
        登录接口
        :return:
        """
        password = cls.md5_encrypt(password)
        url = cls.cache_get(f'{cls.project}_host') + 'api/login'

        allure.attach(str(url), "请求url")
        allure.attach(str(cls.headers), "请求headers")
        json = {"username": username, "password": password}
        response = requests.post(url=url, headers=cls.headers, json=json)
        return response

    @classmethod
    @around()
    def api_reset_password(cls) -> Response:
        """
        重置密码
        :return:
        """


if __name__ == '__main__':
    l = LoginAPI()
    l.cache_set('host', 'https://aigc-dev.growknows.cn/')
    print(l.api_login("maopeng", "123456").json())

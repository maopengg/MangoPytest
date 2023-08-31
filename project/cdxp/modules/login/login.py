# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-08-08 11:25
# @Author : 毛鹏
import allure
import requests
from requests.models import Response

from project.cdxp.cdxp_data_model import CDXPDataModel
from tools.data_processor import DataProcessor
from tools.decorator.response import around


class LoginAPI(DataProcessor):
    headers = {
        'Authorization': 'Basic d2ViQXBwOndlYkFwcA==',
        'Accept': 'application/json, text/plain, */*',
    }
    cdxp_data_model: CDXPDataModel = CDXPDataModel()

    @classmethod
    @around('登录接口')
    def api_login(cls, username, password) -> Response:
        """
        登录接口
        :return:
        """
        api_name = '登录接口'

        password = cls.md5_encrypt(password)
        url = f'{cls.cdxp_data_model.host}/backend/api-auth/oauth/token?username={username}&password={password}&grant_type=password_code'
        allure.attach(str(url), f'{api_name}->请求url')
        allure.attach(str(cls.headers), f'{api_name}->请求headers')

        return requests.post(url=url, headers=cls.headers)

    @classmethod
    @around('重置密码')
    def api_reset_password(cls) -> Response:
        """
        重置密码
        :return:
        """


if __name__ == '__main__':
    r = LoginAPI()
    print(r.api_login("", ""))

# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-08-08 11:25
# @Author : 毛鹏
import requests

from module.login.model import ResponseModel
from tools.decorator.response import response_data
from tools.testdata import GetOrSetTestData


class Login(GetOrSetTestData):

    @classmethod
    @response_data(ResponseModel)
    def api_login(cls, username, password):
        """
        登录接口
        :return:
        """
        password = cls.md5_encrypt(password)
        url = cls.get(
            'host') + f'/backend/api-auth/oauth/token?username={username}&password={password}&grant_type=password_code'
        headers = {
            'Authorization': 'Basic d2ViQXBwOndlYkFwcA==',
            'Accept': 'application/json, text/plain, */*',
        }
        return requests.post(url=url, headers=headers)

    @classmethod
    def api_reset_password(cls):
        """
        重置密码
        :return:
        """


if __name__ == '__main__':
    l = Login()
    l.set('host', 'https://cdxptest.zalldata.cn/')
    print(l.api_login("", ""))

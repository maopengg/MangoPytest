# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-08-08 11:25
# @Author : 毛鹏
import requests
from requests.models import Response

from tools.decorator.response import around
from tools.testdata import GetOrSetTestData


class LoginAPI(GetOrSetTestData):
    headers = {
        'Authorization': 'Basic d2ViQXBwOndlYkFwcA==',
        'Accept': 'application/json, text/plain, */*',
    }

    @classmethod
    @around()
    def api_login(cls, username, password) -> Response:
        """
        登录接口
        :return:
        """
        password = cls.md5_encrypt(password)
        url = cls.get(
            'host') + f'/backend/api-auth/oauth/token?username={username}&password={password}&grant_type=password_code'

        return requests.post(url=url, headers=cls.headers)

    @classmethod
    @around()
    def api_reset_password(cls) -> Response:
        """
        重置密码
        :return:
        """


if __name__ == '__main__':
    l = Login()
    l.set('host', 'https://cdxptest.zalldata.cn/')
    print(l.api_login("", ""))

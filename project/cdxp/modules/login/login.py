# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-08-08 11:25
# @Author : 毛鹏
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
    def api_login(cls, username, password) -> tuple[Response, str, dict] | Response:
        """
        登录接口
        :return:
        """
        password = cls.md5_encrypt(password)
        url = f'{cls.cdxp_data_model.host}/backend/api-auth/oauth/token?username={username}&password={password}&grant_type=password_code'
        response = requests.post(url=url, headers=cls.headers)
        return response, url, cls.headers

    @classmethod
    @around('重置密码')
    def api_reset_password(cls) -> tuple[Response, str, dict] | Response:
        """
        重置密码
        :return:
        """


if __name__ == '__main__':
    r = LoginAPI()
    print(r.api_login("", ""))

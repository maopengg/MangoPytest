# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-08-08 11:25
# @Author : 毛鹏
import json

from requests.models import Response

from auto_test.api_project.cdxp import CDXPDataModel
from models.api_model import ApiDataModel
from tools.data_processor import DataProcessor
from tools.decorator.response import around
from tools.request_base.request_tool import RequestTool


class LoginAPI(DataProcessor, RequestTool):
    headers = {
        'Authorization': 'Basic d2ViQXBwOndlYkFwcA==',
        'Accept': 'application/json, text/plain, */*',
    }
    data_model: CDXPDataModel = CDXPDataModel()

    @classmethod
    @around(7)
    def api_login(cls, data: ApiDataModel) -> ApiDataModel:
        """
        登录接口
        @param data: ApiDataModel
        @return: ApiDataModel
        """
        password = data.test_case_data.case_data.get('password')
        username = data.test_case_data.case_data.get('username')
        group = data.requests_list[data.step]
        url = group.api_data.url
        password = cls.md5_encrypt(password)
        group.request.url = f'{cls.data_model.host}{url}?username={username}&password={password}&grant_type=password_code'
        group.request.headers = cls.headers
        response: ApiDataModel = cls.http_request(data)
        return response

    @classmethod
    @around(0)
    def api_reset_password(cls) -> tuple[Response, int or float, ApiDataModel] | ApiDataModel:
        """
        重置密码
        :return:
        """


if __name__ == '__main__':
    data1 = {'Authorization': 'Bearer null',
             'Accept': 'application/json, text/plain, */*',
             'Content-Type': 'application/json;charset=UTF-8'}
    d = json.dumps(data1)
    print(d)

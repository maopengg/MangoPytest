# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-08-08 11:25
# @Author : 毛鹏
from auto_test.api_project.aigc_saas.data_model import AIGCDataModel
from models.api_model import ApiDataModel
from tools.data_processor import DataProcessor
from tools.decorator.response import around
from tools.request_base.request_tool import RequestTool


class LoginAPI(DataProcessor, RequestTool):
    data_model: AIGCDataModel = AIGCDataModel()
    headers = {
        'Authorization': 'Bearer null',
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json;charset=UTF-8'
    }

    @classmethod
    @around(1)
    def api_login(cls, data: ApiDataModel) -> ApiDataModel:
        """
        登录接口
        :return:
        """
        password = data.test_case_data.case_data.get('password')
        username = data.test_case_data.case_data.get('username')
        group = data.requests_list[data.step]
        group.request.url = f'{cls.data_model.host}{group.api_data.url}'
        group.request.headers = cls.headers
        group.request.json_data = {'username': username,
                                   'password': cls.md5_encrypt(password)}
        response: ApiDataModel = cls.http_request(data)
        return response

    @classmethod
    @around(0)
    def api_reset_password(cls, data: ApiDataModel) -> ApiDataModel:
        """
        重置密码
        :return:
        """

    @classmethod
    @around(2)
    def api_login_out(cls, data: ApiDataModel) -> ApiDataModel:
        """
        退出登录
        :return:
        """
        group = data.requests_list[data.step]
        group.request.url = f'{cls.data_model.host}{group.api_data.url}'
        group.request.headers = cls.get_cache('headers')
        response: ApiDataModel = cls.http_request(data)
        return response


if __name__ == '__main__':
    r = LoginAPI.api_login('maopeng', 'maopeng').json()
    print(r)

# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-08-08 11:25
# @Author : 毛鹏

from requests.models import Response

from models.api_model import ApiDataModel
from tools.base_request.request_tool import RequestTool
from tools.decorator.response import request_data


class LoginAPI(RequestTool):
    headers = {
        'Authorization': 'Basic d2ViQXBwOndlYkFwcA==',
        'Accept': 'application/json, text/plain, */*',
    }

    @request_data
    def api_login(self, data: ApiDataModel) -> ApiDataModel:
        """
        登录接口
        @param data: ApiDataModel
        @return: ApiDataModel
        """
        data.request.headers = self.headers
        data.request.url = f'{data.request.url}?username={data.test_case.other_data["username"]}&password={data.test_case.other_data["password"]}&grant_type=password_code'
        return self.http(data)

    def api_reset_password(self) -> tuple[Response, int or float, ApiDataModel] | ApiDataModel:
        """
        重置密码
        :return:
        """


if __name__ == '__main__':
    pass

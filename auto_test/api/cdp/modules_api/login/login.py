# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-08-08 11:25
# @Author : 毛鹏

from requests.models import Response

from auto_test.api.cdp import CDPDataModel
from models.api_model import ApiDataModel
from tools.decorator.response import request_data
from tools.base_request.request_tool import RequestTool


class LoginAPI(RequestTool):
    headers = {
        'Authorization': 'Basic d2ViQXBwOndlYkFwcA==',
        'Accept': 'application/json, text/plain, */*',
    }
    data_model: CDPDataModel = CDPDataModel()

    @request_data
    def api_login(self, data: ApiDataModel) -> ApiDataModel:
        """
        登录接口
        @param data: ApiDataModel
        @return: ApiDataModel
        """
        # data.test_case.params['password'] = self.data_processor.md5_encrypt(data.test_case.params['password'])
        data.request.headers = self.headers
        data.request.url = f'{data.request.url}?username={data.test_case.other_data["username"]}&password={data.test_case.other_data["password"]}&grant_type=password_code'
        return self.http(data)

    def api_reset_password(self) -> tuple[Response, int or float, ApiDataModel] | ApiDataModel:
        """
        重置密码
        :return:
        """


if __name__ == '__main__':
    data1 = {"base_data": {"test_object": {"id": 1, "project_id": 0, "client_type": 0, "name": "CDP预发环境",
                                           "host": "https://cdxppre.zalldata.cn/", "is_db": 0, "db_user": None,
                                           "db_host": None, "db_port": None, "db_password": None, "db_database": None},
                           "project": {"id": 1, "name": "cdp", "is_notice": 0}, "host": "https://cdxppre.zalldata.cn/",
                           "headers": {"Authorization": "Bearer 98a59a37-a86a-4155-8577-cb7093e4e9c8",
                                       "Accept": "application/json, text/plain, */*", "Currentproject": "precheck",
                                       "Userid": "517", "Service": "zall"}, "is_database_assertion": False,
                           "mysql_config_model": None, "mysql_connect": None, "other_data": None},
             "test_case": {"id": 1, "project_id": 0, "name": "正确的账号，正确的密码，进行登录", "client_type": 0, "method": 0,
                           "url": "/backend/api-auth/oauth/token", "params": {"username": "maopeng@zalldigital.com",
                                                                              "password": "3e194ea226f139e1b8f281c90d349372",
                                                                              "grant_type": "password_code"},
                           "data": None, "json_data": None,
                           "file": None, "other_data": {"username": "maopeng@zalldigital.com",
                                                        "password": "3e194ea226f139e1b8f281c90d349372",
                                                        "grant_type": "password_code"}, "ass_response_whole": None,
                           "ass_response_value": None, "ass_sql": None, "front_sql": None, "posterior_sql": None,
                           "posterior_response": None, "dump_data": None}, "request": None, "response": None}

    LoginAPI().api_login(data=ApiDataModel(**data1))

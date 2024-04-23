# -*- coding: utf-8 -*-
# @Project: MangoServer
# @Description: 
# @Time   : 2024-03-17 19:50
# @Author : 毛鹏
from auto_test.api.mango_testing_platform import MangoDataModel
from models.api_model import ApiDataModel, TestCaseModel
from tools.base_request.request_tool import RequestTool
from tools.decorator.response import request_data


class LoginAPI(RequestTool):
    data_model = MangoDataModel()

    @request_data(3)
    def api_login(self, data: ApiDataModel) -> ApiDataModel:
        """
        登录接口
        @param data: ApiDataModel
        @return: ApiDataModel
        """
        data.request.headers = {}
        return self.http(data)

    def api_reset_password(self) -> ApiDataModel:
        pass


if __name__ == '__main__':
    test_data = ApiDataModel(base_data=MangoDataModel().base_data_model,
                             test_case=TestCaseModel.get_obj(
                                 {"id": 6, "project_id": 7, "name": "正确的账号和密码进行登录", "params": None, "data": None,
                                  "json_data": {"username": "17798339533", "password": "1234567"}, "file": None,
                                  "other_data": None, "ass_response_whole": None, "ass_response_value": None,
                                  "ass_sql": None, "front_sql": None, "posterior_sql": None, "posterior_response": None,
                                  "dump_data": None}))
    test_result: ApiDataModel = LoginAPI().api_login(test_data)
    print(test_result.response)

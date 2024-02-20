# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-09-13 10:27
# @Author : 毛鹏
import json

import allure

from auto_test.api.cdp.modules_api.login.login import LoginAPI
from models.api_model import ApiDataModel
from tools.assertion import Assertion
from tools.data_processor import DataProcessor
from tools.decorator.response import log_decorator


class CaseTool(Assertion):

    @log_decorator
    def case_run(self, func, data: ApiDataModel) -> ApiDataModel:
        """
        公共请求方法
        @param func: 接口函数
        @param data: ApiDataModel
        @return: 响应结果
        """
        res: ApiDataModel = func(data=data)
        self.assertion(res)
        return res

    def assertion(self, data: ApiDataModel):
        allure.attach(str(json.dumps(data.response.response_dict, ensure_ascii=False)), '断言-实际值')
        allure.attach(str(json.dumps(data.test_case.ass_response_whole, ensure_ascii=False)), '断言-期望值')
        if data.test_case.ass_response_whole:
            self.ass_response_whole(data.response.response_dict, data.test_case.ass_response_whole)


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
                           "url": "/backend/api-auth/oauth/token", "params": None,
                           "data": None, "json_data": None,
                           "file": None, "other_data": {"username": "maopeng@zalldigital.com",
                                                        "password": "3e194ea226f139e1b8f281c90d349372",
                                                        "grant_type": "password_code"}, "ass_response_whole": None,
                           "ass_response_value": None, "ass_sql": None, "front_sql": None, "posterior_sql": None,
                           "posterior_response": None, "dump_data": None}, "request": None, "response": None}
    r = LoginAPI()
    r.data_processor = DataProcessor()
    print(CaseTool().case_run(func=r.api_login, data=ApiDataModel(**data1)))

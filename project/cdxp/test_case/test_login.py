# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2021-08-08 15:30
# @Author : 万磊

import allure
import pytest

from models.api_model import ApiDataModel
from project.cdxp.modules.login.login import LoginAPI
from tools.decorator.response import case_data
from tools.request_tool.case_tool import CaseTool


@allure.epic('CDXP')
@allure.feature('登录模块')
class TestLogin(LoginAPI, CaseTool):

    @allure.title('正确的账号，正确的密码，进行登录')
    @case_data(7)
    def test_login01(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.api_login, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.title('正确的账号，错误的密码，进行登录')
    @case_data(8)
    def test_login02(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.api_login, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.title('错误的账号，错误的密码，进行登录')
    @case_data(9)
    def test_login03(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.api_login, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)


if __name__ == '__main__':
    pytest.main(args=[r'D:\GitCode\APIAutoTest\project\cdxp\test_case\test_login.py::TestLogin::test_login01'])

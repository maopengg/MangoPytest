# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-08-08 15:30
# @Author : 毛鹏

import allure
import pytest

from auto_test.api_project.cdxp.modules_api.login.login import LoginAPI
from models.api_model import ApiDataModel
from models.tools_model import DataModel
from tools.assertion import Assertion
from tools.data_processor import DataProcessor
from tools.decorator.response import case_data


@allure.epic('CDP')
@allure.feature('登录模块')
class TestLogin(LoginAPI, Assertion):
    data_processor: DataProcessor = None
    data_model: DataModel = None

    def setup_class(self):
        self.data_processor = DataProcessor()
        self.data_model: DataModel = DataModel()

    @allure.title('正确的账号，正确的密码，进行登录')
    @case_data(7)
    def test_login01(self, data: ApiDataModel):
        self.api_login()
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
    pytest.main(args=[r'D:\GitCode\PytestAutoTest\auto_test\api_project\cdxp\test_case\test_login.py::TestLogin::test_login01'])

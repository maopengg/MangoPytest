# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-08-08 15:30
# @Author : 毛鹏

import allure
import pytest

from auto_test.api.wan_android.modules_api.login import LoginAPI
from models.api_model import ApiDataModel
from tools.base_request.case_tool import CaseTool
from tools.data_processor import DataProcessor
from tools.decorator.response import case_data


@allure.epic('玩安卓API')
@allure.feature('登录模块')
class TestLogin(LoginAPI, CaseTool):
    data_processor: DataProcessor = DataProcessor()

    @allure.title('正确的账号，正确的密码，进行登录')
    @allure.description('测试账号登录')
    @case_data(1)
    def test_login01(self, data: ApiDataModel):
        data = self.case_run(self.api_login, data)
        assert data.response.response_dict['data']['nickname'] == "maopeng"

    @allure.title('正确的账号，错误的密码，进行登录')
    @allure.description('测试账号登录')
    @case_data(2)
    def test_login02(self, data: ApiDataModel):
        data = self.case_run(self.api_login, data)
        assert data.response.response_dict['errorMsg'] == "账号密码不匹配！"

    @allure.title('错误的账号，错误的密码，进行登录')
    @case_data(3)
    def test_login03(self, data: ApiDataModel):
        data = self.case_run(self.api_login, data)
        assert data.response.response_dict['errorMsg'] == "账号密码不匹配！"


if __name__ == '__main__':
    pytest.main([r'D:\GitCode\PytestAutoTest\auto_test\api\cdp\test_case\test_login.py::TestLogin'])

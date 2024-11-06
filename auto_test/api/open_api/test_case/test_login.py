# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2023-08-08 15:30
# @Author : 毛鹏

import allure
import pytest
from mangokit import DataProcessor

from auto_test.api.wan_android.modules_api.login import LoginAPI
from models.api_model import ApiDataModel
from tools.base_request.case_tool import CaseTool
from tools.decorator.response import case_data


@allure.epic('演示-API自动化-常规API-玩安卓')
@allure.feature('登录模块')
class TestLogin(LoginAPI, CaseTool):
    data_processor: DataProcessor = DataProcessor()

    @case_data(1)
    def test_login01(self, data: ApiDataModel):
        data = self.api_login(data)
        assert data.response.response_dict['data']['nickname'] == "maopeng"

    @case_data(2)
    def test_login02(self, data: ApiDataModel):
        data = self.api_login(data)
        assert data.response.response_dict['errorMsg'] == "账号密码不匹配！"

    @case_data(3)
    def test_login03(self, data: ApiDataModel):
        data = self.api_login(data)
        assert data.response.response_dict['errorMsg'] == "账号密码不匹配！"


if __name__ == '__main__':
    pytest.main([r'D:\GitCode\PytestAutoTest\auto_test\api\cdp\test_case\test_login.py::TestLogin::test_login01'])

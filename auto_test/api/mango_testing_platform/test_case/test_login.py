# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-08-08 15:30
# @Author : 毛鹏

import allure
import pytest

from auto_test.api.mango_testing_platform.modules_api.login import LoginAPI
from models.api_model import ApiDataModel
from tools.base_request.case_tool import CaseTool
from tools.data_processor import DataProcessor
from tools.decorator.response import case_data


@allure.epic('芒果测试平台')
@allure.feature('登录模块')
class TestLogin(LoginAPI, CaseTool):
    data_processor: DataProcessor = DataProcessor()

    @allure.title('正确的账号，正确的密码，进行登录')
    @allure.description('测试账号登录')
    @case_data(6)
    def test_login01(self, data: ApiDataModel):
        data = self.api_login(data)
        assert data.response.response_dict['msg'] == "登录成功"
        assert data.response.response_dict['code'] == 200
        assert data.response.response_dict['data'] is not None


if __name__ == '__main__':
    pytest.main(
        [
            r'D:\GitCode\PytestAutoTest\auto_test\api\mango_testing_platform\test_case\test_login.py::TestLogin::test_login01']
    )

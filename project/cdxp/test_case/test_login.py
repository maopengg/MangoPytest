# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-08-08 15:30
# @Author : 毛鹏

import allure
import pytest

from models.api_model import TestCaseModel
from project.cdxp.modules.login.login import LoginAPI
from project.cdxp.modules.login.model import ResponseModel
from tools.decorator.response import testdata


@allure.epic('CDXP')
@allure.feature('登录模块')
class TestLogin(LoginAPI):

    @testdata(7)
    def test_login01(self, test_case: list[TestCaseModel]):
        allure.dynamic.story(test_case[0].name)
        case_data = self.json_loads(test_case[0].case_data)
        result = self.api_login(case_data.get('username'), case_data.get('password'))
        result_dict = ResponseModel.get_obj(result.json())
        assert result_dict.status == 0
        assert result_dict.data.access_token is not None

    @testdata(8)
    def test_login02(self, test_case: list[TestCaseModel]):
        allure.dynamic.story(test_case[0].name)
        case_data = self.json_loads(test_case[0].case_data)
        result = self.api_login(case_data.get('username'), case_data.get('password'))
        result_dict = ResponseModel.get_obj(result.json())
        assert result_dict.status == 1
        assert result_dict.message == '请输入有效的登录账号或密码'

    @testdata(9)
    def test_login03(self, test_case: list[TestCaseModel]):
        allure.dynamic.story(test_case[0].name)
        case_data = self.json_loads(test_case[0].case_data)
        result = self.api_login(case_data.get('username'), case_data.get('password'))
        result_dict = ResponseModel.get_obj(result.json())
        assert result_dict.status == 1
        assert result_dict.message == '请输入有效的登录账号或密码'


if __name__ == '__main__':
    pytest.main(args=[r'D:\GitCode\APIAutoTest\project\cdxp\test_case\test_login.py::TestLogin::test_login01'])

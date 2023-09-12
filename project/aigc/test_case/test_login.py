# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-08-08 15:30
# @Author : 毛鹏

import allure

from models.api_model import TestCaseModel
from project.aigc.modules.login.login import LoginAPI
from project.aigc.modules.login.model import ResponseModel
from tools.assertion.public_assertion import PublicAssertion
from tools.decorator.response import testdata


@allure.epic("AIGC")
@allure.feature("登录模块")
class TestLogin(PublicAssertion, LoginAPI):

    @testdata(1, True)
    def test_login01(self, test_case: list[TestCaseModel]):
        for case_one in test_case:
            allure.dynamic.story(case_one.name)
            case_data = self.json_loads(case_one.case_data)
            result = self.api_login(case_data.get("username"), case_data.get("password"))
            result_dict = ResponseModel.get_obj(result.json())
            self.ass(self.json_loads(case_one.case_ass))
            # assert result_dict.status == 0
            # assert result_dict.data.token is not None

    def ass(self, ass: dict):
        print(f'开始断言：{ass}')
    # @allure.story("登录之后退出登录")
    # def test_login04(self, username, password):
    #     response = LoginAPI.api_login(username, password)
    #     login_dict = ResponseModel.get_obj(response.json())
    #
    #     header = LoginAPI.headers
    #     header['Authorization'] = f'Bearer {login_dict.data.token}'
    #     header['User'] = login_dict.data.userName
    #     header['userId'] = str(login_dict.data.userId)
    #
    #     result = LoginAPI.api_login_out(header)
    #     result_dict = ResponseModel.get_obj(result.json())
    #     assert result_dict.status == 0

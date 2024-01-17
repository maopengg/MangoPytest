# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-08-08 15:30
# @Author : 毛鹏
import copy

import allure

from auto_test.api_project.aigc.modules_api.login.login import LoginAPI
from models.api_model import ApiDataModel
from tools.decorator.response import case_data
from tools.request_base.case_tool import CaseTool


@allure.epic("AIGC")
@allure.feature("1、登录模块")
class TestLogin(LoginAPI, CaseTool):

    @allure.story('1、用户登录')
    @allure.title('1、正确的账号，正确的密码，进行登录')
    @case_data(1)
    def test_login01(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.api_login, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.story('1、用户登录')
    @allure.title('2、正确的账号，错误的密码，进行登录')
    @case_data(2)
    def test_login02(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.api_login, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.story('1、用户登录')
    @allure.title('3、错误的账号，错误的密码，进行登录')
    @case_data(3)
    def test_login03(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.api_login, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.story('2、用户退出')
    @allure.title("1、登录之后退出登录")
    @case_data(4)
    def test_login04(self, data: ApiDataModel):
        with allure.step(f'1.{data.test_case_data.case_step[0]}'):
            data, response_dict = self.case_run(self.api_login, data)
            self.case_ass(response_dict, data.test_case_data, data.db_is_ass, 0)
        with allure.step(f'2.{data.test_case_data.case_step[1]}'):
            data.step = 1
            headers = copy.deepcopy(data.requests_list[0].request.headers)
            headers['Authorization'] = f'Bearer {response_dict.get("token")}'
            headers['User'] = response_dict.get("userName")
            headers['userId'] = str(response_dict.get("userId"))
            self.set_cache('headers', headers)
            data, response_dict = self.case_run(self.api_login_out, data)
            self.case_ass(response_dict, data.test_case_data, data.db_is_ass, 1)

    @allure.story('2、用户退出')
    @allure.title('2、未登录进行退出')
    @case_data(10)
    def test_login05(self, data: ApiDataModel):
        self.case_run(self.api_login_out, data)

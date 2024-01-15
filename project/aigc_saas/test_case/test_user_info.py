# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-12-08 15:17
# @Author : 毛鹏

import allure

from models.api_model import ApiDataModel
from project.aigc_saas.modules.user_info import UserInfoApi
from tools.decorator.response import case_data
from tools.request_tool.case_tool import CaseTool


@allure.epic('AIGC-SAAS')
@allure.feature('登录模块')
class TestLogin(UserInfoApi, CaseTool):

    @allure.title('获取用户信息')
    @case_data(152)
    def test_user_info01(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.get_user_info, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.title('获取企业信息')
    @case_data(153)
    def test_routers01(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.get_routers, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.title('获取角色信息')
    @case_data(154)
    def test_enterprise_info01(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.get_enterprise_info, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

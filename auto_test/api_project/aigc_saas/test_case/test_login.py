# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-12-05 11:52
# @Author : 毛鹏

import allure
import pytest

from auto_test.api_project.aigc_saas.modules_api.login_api import LoginApi
from models.api_model import ApiDataModel
from tools.decorator.response import case_data
from tools.request_base.case_tool import CaseTool


@allure.epic('AIGC-SAAS')
@allure.feature('登录模块')
class TestLogin(LoginApi, CaseTool):

    @allure.title('正确的账号，正确的密码，进行登录')
    @case_data(151)
    def test_login01(self, data: ApiDataModel):
        data.test_case_data.case_data['enterpriseName'] = self.data_model.enterprise
        data.test_case_data.case_data['userName'] = self.data_model.username
        data.test_case_data.case_data['password'] = self.data_model.password
        data.test_case_data.case_data['code'] = self.data_model.verification_code
        data, response_dict = self.case_run(self.login, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)


if __name__ == '__main__':
    pytest.main(args=[r'D:\GitCode\APIAutoTest\project\cdxp\test_case\test_login.py::TestLogin::test_login01'])

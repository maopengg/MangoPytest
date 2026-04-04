# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2023-08-08 15:30
# @Author : 毛鹏

import allure
import pytest

from auto_test.api_mango_mock.abstract.login.login import LoginAPI
from models.api_model import ApiDataModel
from tools.base_request.case_tool import CaseTool
from tools.decorator.response import case_data
from tools.obtain_test_data import ObtainTestData


@allure.epic('演示-API自动化-常规API-MockAPI服务')
class TestLogin(LoginAPI, CaseTool):
    test_data: ObtainTestData = ObtainTestData()

    @case_data([1, 2, 3])
    def test_01(self, data: ApiDataModel):
        data = self.api_login(data)
        assert data.response.response_dict.get('message') is not None


if __name__ == '__main__':
    pytest.main([r'D:\code\MangoPytest\auto_test\api_mango_mock\test_case\test_login\test_login.py::TestLogin'])

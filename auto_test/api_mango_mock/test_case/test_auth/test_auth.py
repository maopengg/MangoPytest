# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2026-01-18 14:04
# @Author : 毛鹏

import allure
import pytest

from auto_test.api_mango_mock.abstract.auth.auth import AuthAPI
from models.api_model import ApiDataModel
from tools.base_request.case_tool import CaseTool
from tools.decorator.response import case_data
from tools.obtain_test_data import ObtainTestData


@allure.epic('演示-API自动化-常规API-MockAPI服务')
@allure.feature('认证模块')
class TestAuth(AuthAPI, CaseTool):
    test_data: ObtainTestData = ObtainTestData()

    @allure.story('用户登录')
    @case_data([1, 2, 3, 4, 5, 6, 7, 8])
    def test_01(self, data: ApiDataModel):
        data = self.api_login(data)
        assert data.response.response_dict.get('message') is not None

    @allure.story('用户注册')
    @case_data([9, 10, 11, 12])
    def test_02(self, data: ApiDataModel):
        data = self.api_register(data)
        assert data.response.response_dict.get('message') is not None


if __name__ == '__main__':
    pytest.main(['-v', 'test_auth.py'])
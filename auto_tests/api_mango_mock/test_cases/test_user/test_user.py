# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2026-01-18 14:05
# @Author : 毛鹏

import allure
import pytest

from auto_tests.api_mango_mock.abstract.user.user import UserAPI
from core.models.api_model import ApiDataModel
from tools.base_request.case_tool import CaseTool
from tools.decorator.response import case_data
from tools.obtain_test_data import ObtainTestData


@allure.epic('演示-API自动化-常规API-MockAPI服务')
class TestUser(UserAPI, CaseTool):
    test_data: ObtainTestData = ObtainTestData()

    @case_data([13, 14, 15, 16, 17])
    def test_01(self, data: ApiDataModel):
        if data.test_case.id in [13, 14]:
            # 获取所有用户
            data = self.get_all_users(data)
        elif data.test_case.id in [15, 16, 17]:
            # 根据ID获取用户
            data = self.get_user_by_id(data)
        assert data.response.response_dict.get('message') is not None

    @case_data([18, 19, 20])
    def test_02(self, data: ApiDataModel):
        data = self.update_user_info(data)
        assert data.response.response_dict.get('message') is not None

    @case_data([21, 22, 23])
    def test_03(self, data: ApiDataModel):
        data = self.delete_user(data)
        assert data.response.response_dict.get('message') is not None


if __name__ == '__main__':
    pytest.main(['-v', 'test_user.py'])

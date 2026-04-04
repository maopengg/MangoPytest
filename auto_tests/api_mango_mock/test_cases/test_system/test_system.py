# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2026-01-18 14:07
# @Author : 毛鹏

import allure
import pytest

from auto_tests.api_mango_mock.abstract.login.login import LoginAPI
from auto_tests.api_mango_mock.abstract.system.system import SystemAPI
from core.models.api_model import ApiDataModel
from core.api.case_tool import CaseTool
from core.decorators.ui import case_data
from core.utils.obtain_test_data  import ObtainTestData


@allure.epic('演示-API自动化-常规API-MockAPI服务')
class TestSystem(SystemAPI, LoginAPI, CaseTool):
    test_data: ObtainTestData = ObtainTestData()

    @case_data([59, 60])
    def test_01(self, data: ApiDataModel):
        data = self.health_check(data)
        assert data.response.response_dict.get('message') is not None

    @case_data([61, 62])
    def test_02(self, data: ApiDataModel):
        data = self.get_server_info(data)
        assert data.response.response_dict.get('message') is not None


if __name__ == '__main__':
    pytest.main(['-v', 'test_system.py'])

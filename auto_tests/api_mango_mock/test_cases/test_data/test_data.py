# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2026-01-18 14:07
# @Author : 毛鹏

import allure
import pytest

from auto_tests.api_mango_mock.abstract.data.data import DataAPI
from models.api_model import ApiDataModel
from tools.base_request.case_tool import CaseTool
from tools.decorator.response import case_data
from tools.obtain_test_data import ObtainTestData


@allure.epic('演示-API自动化-常规API-MockAPI服务')
class TestData(DataAPI, CaseTool):
    test_data: ObtainTestData = ObtainTestData()

    @case_data([55, 56, 57, 58])
    def test_01(self, data: ApiDataModel):
        data = self.submit_data(data)
        assert data.response.response_dict.get('message') is not None


if __name__ == '__main__':
    pytest.main(['-v', 'test_data.py'])

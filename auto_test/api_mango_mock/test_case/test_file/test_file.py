# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2026-01-18 14:06
# @Author : 毛鹏

import allure
import pytest

from auto_test.api_mango_mock.abstract.file.file import FileAPI
from models.api_model import ApiDataModel
from tools.base_request.case_tool import CaseTool
from tools.decorator.response import case_data
from tools.obtain_test_data import ObtainTestData


@allure.epic('演示-API自动化-常规API-MockAPI服务')
@allure.feature('文件管理模块')
class TestFile(FileAPI, CaseTool):
    test_data: ObtainTestData = ObtainTestData()

    @case_data([52, 53, 54])
    def test_01(self, data: ApiDataModel):
        data = self.upload_file(data)
        assert data.response.response_dict.get('message') is not None


if __name__ == '__main__':
    pytest.main(['-v', 'test_file.py'])
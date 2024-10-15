# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2024-04-23 18:09
# @Author : 毛鹏

import allure
import pytest

from auto_test.api.mango_testing_platform.modules_api.index import IndexAPI
from models.api_model import ApiDataModel
from tools.base_request.case_tool import CaseTool
from mangokit import DataProcessor, singleton
from tools.decorator.response import case_data


@allure.epic('芒果测试平台')
@allure.feature('首页')
class TestIndex(IndexAPI, CaseTool):
    data_processor: DataProcessor = DataProcessor()

    @allure.title('获取菜单信息')
    @case_data(11)
    def test_01(self, data: ApiDataModel):
        data = self.api_menu(data)
        self.ass_response_whole(data.response.response_dict, eval(data.test_case.ass_response_whole))


if __name__ == '__main__':
    pytest.main(
        [
            r'D:\GitCode\PytestAutoTest\auto_test\api\mango_testing_platform\test_case\test_login.py::TestLogin::test_login01']
    )

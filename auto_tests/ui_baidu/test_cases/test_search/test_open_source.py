# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-02-20 11:11
# @Author : 毛鹏

import allure

from auto_tests.ui_baidu import base_data_model
from auto_tests.ui_baidu.abstract.home_page import HomePage
from core.models.ui_model import UiDataModel
from core.decorators.ui import case_data
from core.utils.obtain_test_data  import ObtainTestData


@allure.epic('演示-UI自动化-WEB项目-百度')
class TestOpenSource:
    base_data_model = base_data_model
    test_data: ObtainTestData = ObtainTestData()

    @case_data([1, 2])
    def test_01(self, base_data, data: UiDataModel):
        login_page = HomePage(base_data, self.base_data_model, self.test_data)
        login_page.goto()
        login_page.search_keyword(data.test_case.data.get('name'))

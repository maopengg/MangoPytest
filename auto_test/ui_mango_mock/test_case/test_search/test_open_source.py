# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-02-20 11:11
# @Author : 毛鹏

import allure

from auto_test.ui_baidu import base_data_model
from auto_test.ui_baidu.abstract.home_page import HomePage
from auto_test.ui_baidu.abstract.search_results_page import SearchResultsPage
from models.ui_model import UiDataModel
from tools.decorator.ui import case_data
from tools.obtain_test_data import ObtainTestData


@allure.epic('演示-UI自动化-WEB项目-百度')
@allure.feature('搜索自己的开源项目和个人主页')
class TestOpenSource:
    base_data_model = base_data_model
    test_data: ObtainTestData = ObtainTestData()

    @case_data([1, ])
    def test_01(self, base_data, data: UiDataModel):
        login_page = HomePage(base_data, self.base_data_model, self.test_data)
        login_page.goto()
        login_page.search_keyword(data.test_case.data.get('name'))
        search_results_page = SearchResultsPage(base_data, self.base_data_model, self.test_data)
        text = search_results_page.enter_the_project(data.test_case.data.get('name'))
        assert text is not None, f'断言失败，返回的值是：{text}'
        search_results_page.w_wait_for_timeout(3)

    @case_data(3)
    def test_02(self, base_data, data: UiDataModel):
        login_page = HomePage(base_data, self.base_data_model, self.test_data)
        login_page.goto()
        login_page.search_keyword()

    @case_data(case_name='进入到mangopytest主页')
    def test_03(self, base_data, data: UiDataModel):
        login_page = HomePage(base_data, self.base_data_model, self.test_data)
        login_page.goto()
        login_page.search_keyword()

# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2026-03-04 14:15
# @Author : 毛鹏

import allure

from auto_tests.ui_mock import base_data_model
from auto_tests.ui_mock.abstract.home_page import HomePage
from auto_tests.ui_mock.abstract.scroll_page import ScrollPage
from core.utils.obtain_test_data import ObtainTestData


@allure.epic('演示-UI自动化-WEB项目-MockUI服务')
class TestScroll:
    base_data_model = base_data_model
    test_data: ObtainTestData = ObtainTestData()

    @allure.title('演示-滚动页面')
    def test_01(self, base_data):
        """ID: 12 - 演示-滚动页面"""
        data = {"value": "滚动操作测试"}
        self.test_data.set_cache('菜单名称', data.get('value'))
        home_page = HomePage(base_data, self.base_data_model, self.test_data)
        home_page.goto()
        home_page.switch_menu()
        scroll_page = ScrollPage(base_data, self.base_data_model, self.test_data)
        result = scroll_page.test_scroll()
        assert result is not None

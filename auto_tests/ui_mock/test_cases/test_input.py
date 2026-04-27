# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2026-03-04 14:15
# @Author : 毛鹏

import allure

from auto_tests.ui_mock.abstract.home_page import HomePage
from auto_tests.ui_mock.abstract.input_page import InputPage
from core.utils.obtain_test_data import ObtainTestData


@allure.epic('演示-UI自动化-WEB项目-MockUI服务')
class TestInput:
    test_data: ObtainTestData = ObtainTestData()

    @allure.title('演示-不同类型的输入测试')
    def test_01(self, base_data):
        """ID: 7 - 演示-不同类型的输入测试"""
        data = {"value": "输入框测试"}
        self.test_data.set_cache('菜单名称', data.get('value'))
        home_page = HomePage(base_data, self.test_data)
        home_page.goto()
        home_page.switch_menu()
        input_page = InputPage(base_data, self.test_data)
        result = input_page.test_input_types(data.get('value'))
        assert result is not None

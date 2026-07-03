# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2026-03-04 14:15
# @Author : 毛鹏

import allure

from auto_tests.ui_mock.abstract.home_page import HomePage
from auto_tests.ui_mock.abstract.iframe_page import IframePage
from core.utils.obtain_test_data import ObtainTestData


@allure.epic('演示-UI自动化-WEB项目-MockUI服务')
class TestIframe:
    test_data: ObtainTestData = ObtainTestData()

    @allure.title('演示-iframe中得元素定位')
    def test_01(self, base_data):
        """ID: 13 - 演示-iframe中得元素定位"""
        data = {"value": "iframe嵌套测试"}
        self.test_data.set_cache('菜单名称', data.get('value'))
        home_page = HomePage(base_data, self.test_data)
        home_page.goto()
        home_page.switch_menu()
        iframe_page = IframePage(base_data, self.test_data)
        result = iframe_page.test_iframe_element()
        assert result is not None

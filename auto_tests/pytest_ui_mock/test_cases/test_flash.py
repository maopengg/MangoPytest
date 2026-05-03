# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2026-03-04 14:15
# @Author : 毛鹏

import allure

from auto_tests.pytest_ui_mock.page_object.flash_page import FlashPage
from auto_tests.pytest_ui_mock.page_object.home_page import HomePage
from core.utils.obtain_test_data import ObtainTestData


@allure.epic('演示-UI自动化-WEB项目-MockUI服务')
class TestFlash:
    test_data: ObtainTestData = ObtainTestData()

    @allure.title('演示-捕获闪现元素')
    def test_01(self, base_data):
        """ID: 5 - 演示-捕获闪现元素"""
        data = {"value": "闪现元素测试"}
        self.test_data.set_cache('菜单名称', data.get('value'))
        home_page = HomePage(base_data, self.test_data)
        home_page.goto()
        home_page.switch_menu()
        flash_page = FlashPage(base_data, self.test_data)
        result = flash_page.test_flash_element()
        assert result is not None

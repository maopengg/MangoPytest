# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2026-03-04 14:15
# @Author : 毛鹏

import allure

from auto_tests.pytest_ui_mock.page_object.alert_page import AlertPage
from auto_tests.pytest_ui_mock.page_object.home_page import HomePage
from core.utils.obtain_test_data import ObtainTestData


@allure.epic('演示-UI自动化-WEB项目-MockUI服务')
class TestAlert:
    test_data: ObtainTestData = ObtainTestData()

    @allure.title('演示-浏览器弹窗')
    def test_01(self, base_data):
        """ID: 6 - 演示-浏览器弹窗"""
        data = {"value": "弹窗测试"}
        self.test_data.set_cache('菜单名称', data.get('value'))
        home_page = HomePage(base_data, self.test_data)
        home_page.goto()
        home_page.switch_menu()

        alert_page = AlertPage(base_data, self.test_data)

        # 测试alert弹窗
        alert_page.test_alert()

        # 测试confirm弹窗
        alert_page.test_confirm()

        # 测试prompt弹窗
        alert_page.test_prompt()

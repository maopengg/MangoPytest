# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-02-20 11:11
# @Author : 毛鹏

import allure
import pytest

from auto_tests.ui_baidu import base_data_model
from auto_tests.ui_baidu.abstract.home_page import HomePage
from core.utils.obtain_test_data import ObtainTestData


@allure.epic('演示-UI自动化-WEB项目-百度')
class TestOpenSource:
    base_data_model = base_data_model
    test_data: ObtainTestData = ObtainTestData()

    @allure.title('搜索芒果测试平台')
    def test_01(self, base_data):
        """ID: 1 - 搜索芒果测试平台"""
        data = {"name": "芒果测试平台"}
        login_page = HomePage(base_data, self.base_data_model, self.test_data)
        login_page.goto()
        login_page.search_keyword(data.get('name'))

    @allure.title('搜索PytestAutoTest')
    def test_02(self, base_data):
        """ID: 2 - 搜索PytestAutoTest"""
        data = {"name": "PytestAutoTest"}
        login_page = HomePage(base_data, self.base_data_model, self.test_data)
        login_page.goto()
        login_page.search_keyword(data.get('name'))

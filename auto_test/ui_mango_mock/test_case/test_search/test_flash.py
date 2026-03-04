# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2026-03-04 14:15
# @Author : 毛鹏

import allure

from auto_test.ui_mango_mock import base_data_model
from auto_test.ui_mango_mock.abstract.flash_page import FlashPage
from auto_test.ui_mango_mock.abstract.home_page import HomePage
from models.ui_model import UiDataModel
from tools.decorator.ui import case_data
from tools.obtain_test_data import ObtainTestData


@allure.epic('演示-UI自动化-WEB项目-MockUI服务')
@allure.feature('闪现元素捕获')
class TestFlash:
    base_data_model = base_data_model
    test_data: ObtainTestData = ObtainTestData()

    @allure.story('闪现元素测试')
    @case_data([5])
    def test_01(self, base_data, data: UiDataModel):
        """测试捕获闪现元素"""
        self.test_data.set_cache('菜单名称', data.test_case.data.get('value'))
        home_page = HomePage(base_data, self.base_data_model, self.test_data)
        home_page.goto()
        home_page.switch_menu()
        flash_page = FlashPage(base_data, self.base_data_model, self.test_data)
        result = flash_page.test_flash_element()
        assert result is not None


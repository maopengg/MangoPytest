# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-02-20 11:11
# @Author : 毛鹏

import allure

from auto_test.ui_baidu import base_data
from auto_test.ui_baidu.components.components.home import HomePage
from auto_test.ui_baidu.components.components.open_source import OpenSourcePage
from models.ui_model import UiDataModel
from tools.decorator.ui import case_data
from tools.obtain_test_data import ObtainTestData


@allure.epic('演示-UI自动化-WEB项目-Gitee')
@allure.feature('搜索自己的开源项目')
class TestOpenSource:
    base_data = base_data
    test_data: ObtainTestData = ObtainTestData()

    @case_data([1, 2])
    def test_01(self, execution_context, data: UiDataModel):
        login_page = HomePage(execution_context, base_data, self.test_data)
        login_page.goto()
        login_page.click_open_source()
        open_source_page = OpenSourcePage(execution_context, base_data, self.test_data)
        open_source_page.search_for_open_source_projects(data.test_case.data.get('name'))
        open_source_page.w_wait_for_timeout(3)

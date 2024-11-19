# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-02-20 11:11
# @Author : 毛鹏

import allure
from tools.obtain_test_data import ObtainTestData
from auto_test.ui.gitee import GiteeDataModel
from auto_test.ui.gitee.page_object.home import HomePage
from auto_test.ui.gitee.page_object.open_source import OpenSourcePage
from models.ui_model import UiDataModel
from tools.decorator.ui import case_data


@allure.epic('演示-UI自动化-WEB项目-Gitee')
@allure.feature('搜索自己的开源项目')
class TestOpenSource:
    data_model: GiteeDataModel = GiteeDataModel()
    test_data: ObtainTestData = ObtainTestData()

    @case_data([1, 2])
    def test_01(self, execution_context, data: UiDataModel):
        login_page = HomePage(execution_context, self.data_model)
        login_page.w_goto()
        login_page.click_open_source()
        open_source_page = OpenSourcePage(execution_context, self.data_model)
        open_source_page.search_for_open_source_projects(data.test_case.data.get('name'))
        open_source_page.w_wait_for_timeout(3)

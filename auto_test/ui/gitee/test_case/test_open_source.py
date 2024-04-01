# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2024-02-20 11:11
# @Author : 毛鹏
import time

import allure

from auto_test.ui import *
from auto_test.ui.gitee.page_object.home import HomePage
from auto_test.ui.gitee import GiteeDataModel
from auto_test.ui.gitee.page_object.open_source import OpenSourcePage


@allure.epic('Gitee')
@allure.feature('搜索自己的开源项目')
class TestOpenSource:

    def setup_class(self):
        self.data_model: GiteeDataModel = GiteeDataModel()

    def teardown_class(self):
        pass

    @allure.title('搜索芒果测试平台，并断言项目可以被搜索到')
    @pytest.mark.parametrize("name", ["芒果测试平台"])
    def test_open1(self, setup_context_page, name):
        login_page = HomePage(setup_context_page, self.data_model)
        login_page.w_goto()
        login_page.click_open_source()
        open_source_page = OpenSourcePage(setup_context_page, self.data_model)
        open_source_page.search_for_open_source_projects(name)
        time.sleep(3)

    @allure.title('搜索PytestAutoTest，并断言项目可以被搜索到')
    @pytest.mark.parametrize("name", ["PytestAutoTest"])
    def test_open2(self, setup_context_page, name):
        login_page = HomePage(setup_context_page, self.data_model)
        login_page.w_goto()
        login_page.click_open_source()
        open_source_page = OpenSourcePage(setup_context_page, self.data_model)
        open_source_page.search_for_open_source_projects(name)
        time.sleep(3)


if __name__ == '__main__':
    pytest.main(
        [r'D:\GitCode\PytestAutoTest\auto_test\ui\gitee\test_case\test_open_source.py::TestOpenSource'])

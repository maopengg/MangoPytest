# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2024-02-20 11:11
# @Author : 毛鹏
import time

import allure

from auto_test.ui import *
from auto_test.ui.wan_android import WanAndroidDataModel


@allure.epic('Gitee')
@allure.feature('查看开源项目')
class TestLogin:

    def setup_class(self):
        self.data_model: WanAndroidDataModel = WanAndroidDataModel()

    def teardown_class(self):
        pass

    @allure.title('搜索芒果测试平台，并断言项目可以被搜索到')
    @pytest.mark.parametrize("username, password", [("maopeng", "729164035")])
    def test_login1(self, setup_context_page, username, password):
        login_page = LoginPage(setup_context_page, self.data_model)
        login_page.w_goto()
        login_page.login(username, password)
        time.sleep(3)

    @allure.title('搜索PytestAutoTest，并断言项目可以被搜索到')
    @pytest.mark.parametrize("username, password", [("maopeng", "729164035")])
    def test_login1(self, setup_context_page, username, password):
        login_page = LoginPage(setup_context_page, self.data_model)
        login_page.w_goto()
        login_page.login(username, password)
        time.sleep(3)


if __name__ == '__main__':
    pytest.main(
        [r'D:\GitCode\PytestAutoTest\auto_test\ui\wan_android\test_case\test_login.py::TestLogin'])

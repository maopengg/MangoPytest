# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2024-02-20 11:11
# @Author : 毛鹏
import allure
import time

from auto_test.ui import *
from auto_test.ui.wan_android import WanAndroidDataModel
from auto_test.ui.wan_android.page_object.login import LoginPage


@allure.epic('演示-UI自动化-WEB项目-玩安卓')
@allure.feature('登录模块')
class TestLogin:

    def setup_class(self):
        self.data_model: WanAndroidDataModel = WanAndroidDataModel()

    def teardown_class(self):
        pass

    @allure.title('正确的账号，正确的密码，进行登录')
    @pytest.mark.parametrize("username, password", [("maopeng", "729164035")])
    def test_login1(self, setup_context_page, username, password):
        login_page = LoginPage(setup_context_page, self.data_model)
        login_page.w_goto()
        login_page.login(username, password)
        time.sleep(3)

    @allure.title('正确的账号，错误的密码，进行登录')
    @pytest.mark.parametrize("username, password", [("maopeng", "7291640351")])
    def test_login2(self, setup_context_page, username, password):
        login_page = LoginPage(setup_context_page, self.data_model)
        login_page.w_goto()
        login_page.login(username, password)
        time.sleep(3)


if __name__ == '__main__':
    pytest.main(
        [r'D:\GitCode\PytestAutoTest\auto_test\ui\wan_android\test_case\test_login.py::TestLogin'])

# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-02-20 11:11
# @Author : 毛鹏
import allure

from auto_test.ui.wan_android import WanAndroidDataModel
from auto_test.ui.wan_android.page_object.login import LoginPage
from tools.decorator.ui import case_data


@allure.epic('演示-UI自动化-WEB项目-玩安卓')
@allure.feature('登录模块')
class TestLogin:

    def setup_class(self):
        self.data_model: WanAndroidDataModel = WanAndroidDataModel()

    def teardown_class(self):
        pass

    @case_data('玩安卓登录用例', [
        {'username': 'maopeng', 'password': '729164035'},
        {'username': 'maopeng', 'password': '7291640351'},
        {'username': 'maopeng1', 'password': '729164035'},
    ])
    def test_login1(self, setup_context_page, data):
        username, password = data['username'], data['password']
        login_page = LoginPage(setup_context_page, self.data_model)
        login_page.w_goto()
        login_page.login(username, password)

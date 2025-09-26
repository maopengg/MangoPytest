# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-02-20 11:11
# @Author : 毛鹏
import allure

from auto_test.ui_wan_android import base_data
from auto_test.ui_wan_android.components.login.login import LoginPage
from models.ui_model import UiDataModel
from tools.decorator.ui import case_data
from tools.obtain_test_data import ObtainTestData


@allure.epic('演示-UI自动化-WEB项目-玩安卓')
@allure.feature('登录模块')
class TestLogin:
    base_data = base_data
    test_data: ObtainTestData = ObtainTestData()

    @case_data([3, 4, 5])
    def test_01(self, execution_context, data: UiDataModel):
        login_page = LoginPage(execution_context, base_data, self.test_data)
        login_page.goto_url()
        username = data.test_case.data.get('username')
        password = data.test_case.data.get('password')
        login_page.login(username, password)

    # 修改用户的昵称，断言修改成功后再修改回原来的
    @case_data(6)
    def test_02(self, execution_context, data: UiDataModel):
        login_page = LoginPage(execution_context, base_data, self.test_data)
        login_page.goto_url()
        username = data.test_case.data.get('username')
        password = data.test_case.data.get('password')
        login_page.login(username, password)
        new_username = self.test_data.str_uuid()
        old_username, _username = login_page.edit_user_info(new_username)
        assert old_username == username
        assert _username == new_username
        old_username, _username = login_page.edit_user_info(username)
        assert old_username == new_username
        assert _username == username

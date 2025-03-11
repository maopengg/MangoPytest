# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-02-20 11:11
# @Author : 毛鹏
import allure

from auto_test.ui_wan_android import ui_project_data_model, UiProjectDataModel
from auto_test.ui_wan_android.components.login.login import LoginPage
from models.ui_model import UiDataModel
from tools.decorator.ui import case_data
from tools.obtain_test_data import ObtainTestData


@allure.epic('演示-UI自动化-WEB项目-玩安卓')
@allure.feature('登录模块')
class TestLogin:
    data_model: UiProjectDataModel = ui_project_data_model
    test_data: ObtainTestData = ObtainTestData()

    @case_data([3, 4, 5])
    def test_01(self, execution_context, data: UiDataModel):
        login_page = LoginPage(execution_context, self.data_model, self.test_data)
        login_page.goto_url()
        login_page.login(data.test_case.data.get('username'), data.test_case.data.get('password'))

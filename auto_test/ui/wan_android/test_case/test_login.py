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

def custom_test_decorator(title, parametrize_values):
    def decorator(func):
        @allure.title(title)
        @pytest.mark.parametrize("username, password", parametrize_values)
        @pytest.mark.asyncio
        async def wrapper(self, setup_context_page, username, password):
            return await func(self, setup_context_page, username, password)
        return wrapper
    return decorator


# 定义用例参数
login_cases = [
    ("maopeng", "729164035"),
    ("maopeng", "7291640351"),
    ("maopeng", "7291640351")
]
@allure.epic('演示-UI自动化-WEB项目-玩安卓')
@allure.feature('登录模块')
class TestLogin:

    def setup_class(self):
        self.data_model: WanAndroidDataModel = WanAndroidDataModel()

    def teardown_class(self):
        pass

    @custom_test_decorator('玩安卓登录用例', login_cases)
    async def test_login1(self, setup_context_page, username, password):
        login_page = LoginPage(await setup_context_page, self.data_model)
        await login_page.w_goto()
        await login_page.login(username, password)
        time.sleep(3)


if __name__ == '__main__':
    pytest.main(
        [r'D:\GitCode\PytestAutoTest\auto_test\ui\wan_android\test_case\test_login.py::TestLogin'])

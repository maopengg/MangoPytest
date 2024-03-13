# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2024-02-20 11:11
# @Author : 毛鹏
import allure
import pytest

from auto_test.ui.wan_android.page_object.login.login import LoginPage
from models.ui_model import WEBConfigModel
from tools.base_page.web.new_browser import NewDrowser
from tools.data_processor import DataProcessor


@pytest.fixture(scope='function')
def setup_context_page():
    data = NewDrowser(WEBConfigModel(browser_type=0,
                                     browser_port='登录',
                                     browser_path=None,
                                     is_headless=False,
                                     is_header_intercept=False,
                                     host=None,
                                     project_id=None))
    context, page = data.new_context(data.new_browser())
    yield context, page
    context.close()
    page.close()


@allure.epic('玩安卓')
@allure.feature('登录模块')
class TestLogin:

    def setup_class(self):
        self.data_processor = DataProcessor()

    def teardown_class(self):
        pass

    @allure.title('正确的账号，正确的密码，进行登录')
    @pytest.mark.parametrize("username, password", [("maopeng", "729164035")])
    def test_login1(self, setup_context_page, username, password):
        context, page = setup_context_page
        login_page = LoginPage((context, page), self.data_processor)
        login_page.w_goto(login_page.url)
        login_page.login(username, password)

    @allure.title('正确的账号，错误的密码，进行登录')
    @pytest.mark.parametrize("username, password", [("maopeng", "7291640351")])
    def test_login2(self, setup_context_page, username, password):
        context, page = setup_context_page
        login_page = LoginPage((context, page), self.data_processor)
        login_page.w_goto(login_page.url)
        login_page.login(username, password)


if __name__ == '__main__':
    pytest.main(
        [r'D:\GitCode\PytestAutoTest\auto_test\ui\wan_android\test_case\test_login.py::TestLogin'])

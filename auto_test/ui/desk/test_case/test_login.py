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


# @pytest.fixture(scope="module")
@pytest.fixture()
def context_page():
    data = NewDrowser(WEBConfigModel(browser_type=0,
                                     browser_port='登录',
                                     browser_path='C:\Program Files\Google\Chrome\Application\chrome.exe',
                                     is_headless=False,
                                     is_header_intercept=False,
                                     host=None,
                                     project_id=None))
    context, page = data.new_context(data.new_browser())
    return context, page


@allure.epic('CDP')
@allure.feature('登录模块')
class TestLogin:
    data_processor = DataProcessor()

    @allure.title('正确的账号，正确的密码，进行登录')
    @pytest.mark.parametrize("username, password", [("user1", "pass1")])
    def test_example(self, context_page, username, password):
        login_page = LoginPage(context_page, self.data_processor)
        login_page.login(username, password)


if __name__ == '__main__':
    pytest.main(
        [r'D:\GitCode\PytestAutoTest\auto_test\ui\wan_android\test_case\test_login.py::TestLogin::test_example'])

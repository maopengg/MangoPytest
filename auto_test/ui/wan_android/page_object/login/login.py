# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2024-02-20 11:04
# @Author : 毛鹏
from playwright.sync_api import Page, BrowserContext

from models.ui_model import WEBConfigModel
from tools.base_page import BasePage
from tools.base_page.web.new_browser import NewDrowser
from tools.data_processor import DataProcessor


class LoginPage(BasePage):
    """
    页面元素
    """
    url = "https://wanandroid.com/index"

    def __init__(self, context_page: tuple[BrowserContext, Page], data_processor: DataProcessor):
        super().__init__(4, '登录', context_page, data_processor)

    # 查询操作
    def login(self, username: str, password: str):
        self.w_click(self.element('登录按钮'))
        self.w_input(self.element('用户名'), username)
        self.w_input(self.element('密码'), password)
        self.w_click(self.element('登录'))


if __name__ == '__main__':
    data = NewDrowser(
        WEBConfigModel(browser_type=0,
                       browser_port='登录',
                       browser_path=None,
                       is_headless=False,
                       is_header_intercept=False,
                       host=None,
                       project_id=None))
    login_page = LoginPage(data.new_context(data.new_browser()), data_processor=DataProcessor())
    login_page.w_goto(login_page.url)
    login_page.login('maopeng', '729164035')

# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2024-02-20 11:04
# @Author : 毛鹏
import time

from models.ui_model import WEBConfigModel
from tools.base_page import BasePage
from tools.base_page.web.new_browser import NewDrowser
from tools.data_processor import DataProcessor


class LoginPage(BasePage):
    """
    页面元素
    """
    url = "http:8088/portal/"

    # 查询操作
    def login(self, username: str, password: str):
        self.w_goto(self.url)
        self.w_input(self.w_find_element(self.element_model('用户名')), username)
        self.w_input(self.w_find_element(self.element_model('密码')), password)
        self.w_click(self.w_find_element(self.element_model('登录')))
        time.sleep(5)


if __name__ == '__main__':
    data = NewDrowser(WEBConfigModel(browser_type=0,
                                     browser_port='登录',
                                     browser_path='C:\Program Files\Google\Chrome\Application\chrome.exe',
                                     is_headless=False,
                                     is_header_intercept=False,
                                     host=None,
                                     project_id=None))
    LoginPage(data.new_context(data.new_browser()), data_processor=DataProcessor()).login('zesk_system', 'zesk8888')

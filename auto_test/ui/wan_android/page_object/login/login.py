# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2024-02-20 11:04
# @Author : 毛鹏

from enums.ui_enum import ElementExpEnum
from models.ui_model import ElementModel, WEBConfigModel
from tools.base_page import BasePage
from tools.base_page.web.new_browser import NewDrowser


class LoginPage(BasePage):
    """
    页面元素
    """
    # 百度首页链接
    url = "https://wanandroid.com/"
    # 搜索框
    home_login = '//a[text()="登录"]'
    # "百度一下"按钮框
    username = '//input[@placeholder="请输入用户名"]'
    password = '//input[@placeholder="请输入密码"]'
    button_login = '//p[@class="opt_p"]/span[text()="登录"]'

    # 查询操作
    def login(self, username: str, password: str):
        self.w_goto(self.url)
        self.w_click(self.w_find_element(ElementModel(id=0,
                                                      name='登录',
                                                      locator=self.home_login,
                                                      method=ElementExpEnum.XPATH.value,
                                                      subscript=0,
                                                      sleep=0,
                                                      is_iframe=0)))
        self.w_input(self.w_find_element(ElementModel(id=0,
                                                      name='登录',
                                                      locator=self.username,
                                                      method=ElementExpEnum.XPATH.value,
                                                      subscript=0,
                                                      sleep=0,
                                                      is_iframe=0)), username)
        self.w_input(self.w_find_element(ElementModel(id=0,
                                                      name='登录',
                                                      locator=self.password,
                                                      method=ElementExpEnum.XPATH.value,
                                                      subscript=0,
                                                      sleep=0,
                                                      is_iframe=0)), password)
        self.w_click(self.w_find_element(ElementModel(id=0,
                                                      name='登录',
                                                      locator=self.button_login,
                                                      method=ElementExpEnum.XPATH.value,
                                                      subscript=0,
                                                      sleep=0,
                                                      is_iframe=0)))


if __name__ == '__main__':
    data = NewDrowser(WEBConfigModel(browser_type=0,
                                     browser_port='登录',
                                     browser_path='C:\Program Files\Google\Chrome\Application\chrome.exe',
                                     is_headless=False,
                                     is_header_intercept=False,
                                     host=None,
                                     project_id=None))

    context, page = data.new_context(data.new_browser())
    LoginPage(page=page, context=context).login('17798339533', 'm729164035')

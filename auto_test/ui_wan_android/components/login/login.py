# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-02-20 11:04
# @Author : 毛鹏
from urllib.parse import urljoin

from playwright.sync_api import Page, BrowserContext

from auto_test.project_config import ProjectEnum
from models.ui_model import UiProjectDataModel
from tools.base_object.base_object import WebBaseObject
from tools.obtain_test_data import ObtainTestData


class LoginPage(WebBaseObject):
    """
    登录页面
    """

    def __init__(self,
                 context_page: tuple[BrowserContext, Page],
                 data_model: UiProjectDataModel,
                 test_data: ObtainTestData):
        self.project_name = ProjectEnum.WanAndroid.value
        self.module_name = '登录'
        self.page_name = '登录'
        super().__init__(self.project_name, self.module_name, self.page_name, context_page, test_data)
        self.url = urljoin(data_model.base_data.host, '/index')

    def goto_url(self):
        self.w_goto(self.url)

    def login(self, username: str, password: str):
        self.w_click(self.element('登录按钮'))
        self.w_input(self.element('用户名'), username)
        self.w_input(self.element('密码'), password)
        self.w_click(self.element('登录'))

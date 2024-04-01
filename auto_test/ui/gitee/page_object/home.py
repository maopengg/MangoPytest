# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2024-04-01 16:04
# @Author : 毛鹏
from urllib.parse import urljoin

from playwright.sync_api import Page, BrowserContext

from auto_test.ui.gitee import GiteeDataModel
from tools.base_page import BasePage


class HomePage(BasePage):
    """
    gitee首页
    """

    def __init__(self, context_page: tuple[BrowserContext, Page], data_model: GiteeDataModel):
        project_id = 6
        module_name = '首页'
        super().__init__(project_id, module_name, context_page, data_model.data_processor)
        self.url = urljoin(data_model.base_data_model.host, '')

    def click_open_source(self):
        self.w_click(self.element('菜单-开源'))

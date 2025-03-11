# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-04-01 16:04
# @Author : 毛鹏
from urllib.parse import urljoin

from playwright.sync_api import Page, BrowserContext

from auto_test.project_config import ProjectEnum
from auto_test.ui_baidu import GiteeDataModel
from tools.base_page import BasePage


class HomePage(BasePage):
    """
    gitee首页
    """

    def __init__(self, context_page: tuple[BrowserContext, Page], data_model: GiteeDataModel):
        project_name = ProjectEnum.Gitee.value
        module_name = '首页'
        super().__init__(project_name, module_name, context_page, data_model.test_data)
        self.url = urljoin(data_model.base_data.host, '')

    def click_open_source(self):
        self.w_click(self.element('菜单-开源'))

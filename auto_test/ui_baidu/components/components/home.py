# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-04-01 16:04
# @Author : 毛鹏
from urllib.parse import urljoin

from playwright.sync_api import Page, BrowserContext

from auto_test.project_config import ProjectEnum
from models.ui_model import UiProjectDataModel
from tools.base_object.base_object import WebBaseObject
from tools.obtain_test_data import ObtainTestData


class HomePage(WebBaseObject):
    """
    gitee首页
    """

    def __init__(self,
                 context_page: tuple[BrowserContext, Page],
                 data_model: UiProjectDataModel,
                 test_data: ObtainTestData):
        project_name = ProjectEnum.Gitee.value
        module_name = '首页'
        page_name = '首页'
        super().__init__(project_name, module_name, page_name, context_page, test_data)
        self.url = urljoin(data_model.base_data.host, '')

    def goto(self):
        self.w_goto(self.url)

    def click_open_source(self):
        self.w_click(self.element('菜单-开源'))

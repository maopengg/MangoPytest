# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-04-01 16:04
# @Author : 毛鹏
import time
from urllib.parse import urljoin

from mangoautomation.uidrives import BaseData
from playwright.sync_api import Page, BrowserContext

from auto_test.project_config import ProjectEnum
from models.tools_model import BaseDataModel
from tools.base_object.base_object import WebBaseObject
from tools.log import log
from tools.obtain_test_data import ObtainTestData


class SearchResultsPage(WebBaseObject):
    """
    搜索结果页
    """

    def __init__(self,
                 base_data: BaseData,
                 base_data_model: BaseDataModel,
                 test_data: ObtainTestData):
        project_name = ProjectEnum.BAIDU.value
        module_name = '搜索结果'
        page_name = '搜索结果'
        self.base_data_model = base_data_model
        self.base_data = base_data
        self.test_data = test_data
        super().__init__(project_name, module_name, page_name, self.base_data, self.test_data)
        self.url = urljoin(self.base_data_model.test_object.host, '')

    def goto(self):
        self.w_goto(self.url)

    def w_open_new_tab_and_switch_(self, locating):
        """点击并打开新页签"""
        with self.base_data.context.expect_page() as new_page_info:
            locating.click()
        new_page = new_page_info.value
        new_page.bring_to_front()
        self.base_data.page = new_page
        new_page.wait_for_load_state("domcontentloaded")

    def enter_the_project(self, project_name: str):
        self.w_open_new_tab_and_switch_(self.element(project_name))
        text = self.w_get_text(self.element('获取介绍'))
        return text

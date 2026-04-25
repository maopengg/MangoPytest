# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-04-01 16:04
# @Author : 毛鹏
from urllib.parse import urljoin

from playwright.sync_api import Page, BrowserContext

from auto_tests.project_config import ProjectEnum
from auto_tests.ui_baidu.config import settings
from core.ui import WebBaseObject
from core.utils.obtain_test_data  import ObtainTestData


class GiteePage(WebBaseObject):
    """
    Gitee页面
    """

    def __init__(self,
                 context_page: tuple[BrowserContext, Page],
                 test_data: ObtainTestData):
        project_name = ProjectEnum.BAIDU.value
        module_name = 'Gitee'
        page_name = 'Gitee页面'
        super().__init__(project_name, module_name, page_name, context_page, test_data)
        self.url = settings.BASE_URL

    def goto(self):
        self.w_goto(self.url)

    def click_open_source(self):
        self.w_click(self.element('菜单-开源'))

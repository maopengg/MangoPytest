# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2024-04-01 16:04
# @Author : 毛鹏
from urllib.parse import urljoin

from playwright.sync_api import Page, BrowserContext

from auto_test.ui.gitee import GiteeDataModel
from tools.base_page import BasePage


class OpenSourcePage(BasePage):
    """
    gitee首页
    """

    def __init__(self, context_page: tuple[BrowserContext, Page], data_model: GiteeDataModel):
        project_id = 6
        module_name = '开源'
        super().__init__(project_id, module_name, context_page, data_model.data_processor)
        self.url = urljoin(data_model.base_data_model.host, '/explore')

    async def search_for_open_source_projects(self, name: str):
        await self.w_input(await self.element('开源搜索框'), name)
        await self.w_click(await self.element('搜索按钮'))

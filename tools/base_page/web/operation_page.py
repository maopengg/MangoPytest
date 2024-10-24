# -*- coding: utf-8 -*-
# @Project: 芒果测试平台# @Description:
# @Time   : 2023-04-25 22:33
# @Author : 毛鹏

from playwright.sync_api import Locator
from playwright.sync_api import Page, BrowserContext


class PlaywrightPageOperation:
    """页面操作"""
    page: Page = None
    context: BrowserContext = None

    def w_switch_tabs(self, individual: int):
        """切换页签"""
        pages = self.context.pages
        pages[int(individual)].bring_to_front()
        self.page = pages[int(individual)]

    def w_close_current_tab(self):
        """关闭当前页签"""
        pages = self.context.pages
        pages[-1].close()
        self.page = pages[0]

    def open_new_tab_and_switch(self, locating: Locator):
        """点击并打开新页签"""
        locating.click()
        pages = self.context.pages
        new_page = pages[-1]
        new_page.bring_to_front()
        self.page = new_page

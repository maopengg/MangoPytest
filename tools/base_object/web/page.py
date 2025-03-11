# -*- coding: utf-8 -*-
# @Project: MangoActuator
# @Description: 
# @Time   : 2023-04-25 22:33
# @Author : 毛鹏
import time
from playwright.async_api import Locator

from tools.base_object.web.web_object.web_object import WebBaseObject


class PlaywrightPage(WebBaseObject):
    """页面操作"""

    def w_switch_tabs(self, individual: int):
        """切换页签"""
        pages = self.context.pages
        pages[int(individual)].bring_to_front()
        self.page = pages[int(individual)]
        time.sleep(1)

    def w_close_current_tab(self):
        """关闭当前页签"""
        time.sleep(2)
        pages = self.context.pages
        pages[-1].close()
        self.page = pages[0]

    def open_new_tab_and_switch(self, locating: Locator):
        """点击并打开新页签"""
        locating.click()
        time.sleep(2)
        pages = self.context.pages
        new_page = pages[-1]
        new_page.bring_to_front()
        self.page = new_page
        time.sleep(1)

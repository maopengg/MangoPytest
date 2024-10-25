# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: # @Time   : 2023-04-25 22:33
# @Author : 毛鹏
import ctypes
import os
import string
import threading
from typing import Optional

from mangokit import singleton
from playwright.sync_api import sync_playwright, Page, BrowserContext, Browser, Error

from enums.ui_enum import BrowserTypeEnum
from exceptions.error_msg import ERROR_MSG_0039, ERROR_MSG_0040
from exceptions.ui_exception import BrowserPathError
from models.ui_model import WEBConfigModel
from settings.settings import BROWSER_IS_MAXIMIZE


@singleton
class NewBrowser:

    def __init__(self, web_config: WEBConfigModel):
        self.web_config = web_config
        self.browser_path = ['chrome.exe', 'msedge.exe', 'firefox.exe', '苹果', '360se.exe']
        self.browser: Optional[Browser] = None
        self.lock = threading.Lock()

    def new_browser(self):
        playwright = sync_playwright().start()
        if self.web_config.browser_type == BrowserTypeEnum.CHROMIUM or self.web_config.browser_type == BrowserTypeEnum.EDGE:
            browser = playwright.chromium
        elif self.web_config.browser_type == BrowserTypeEnum.FIREFOX:
            browser = playwright.firefox
        elif self.web_config.browser_type == BrowserTypeEnum.WEBKIT:
            browser = playwright.webkit
        else:
            raise BrowserPathError(*ERROR_MSG_0039)
        try:
            self.web_config.browser_path = self.web_config.browser_path if self.web_config.browser_path else self.__search_path()
            if BROWSER_IS_MAXIMIZE:
                self.browser = browser.launch(headless=self.web_config.is_headless,
                                              executable_path=self.web_config.browser_path,
                                              args=['--start-maximized'])
            else:
                self.browser = browser.launch(headless=self.web_config.is_headless,
                                              executable_path=self.web_config.browser_path)
        except Error as error:
            raise BrowserPathError(*ERROR_MSG_0040, error=error)

    def new_context_page(self) -> tuple[BrowserContext, Page]:
        with self.lock:
            if self.browser is None:
                self.new_browser()

        context = self.browser.new_context(no_viewport=True)
        return context, context.new_page()

    def __search_path(self, ):
        drives = []
        for letter in string.ascii_uppercase:
            drive = f"{letter}:\\"
            if ctypes.windll.kernel32.GetDriveTypeW(drive) == 3:
                drives.append(drive)
        for i in drives:
            for root, dirs, files in os.walk(i):
                if self.browser_path[self.web_config.browser_type.value] in files:
                    return os.path.join(root, self.browser_path[self.web_config.browser_type.value])


if __name__ == '__main__':
    browser = NewBrowser(WEBConfigModel(browser_type=BrowserTypeEnum.CHROMIUM))
    for i in range(100):
        context, page = browser.new_context_page()
        page.goto('https://www.baidu.com')

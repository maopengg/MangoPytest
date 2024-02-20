# -*- coding: utf-8 -*-
# @Project: MangoActuator
# @Description: 
# @Time   : 2023-04-25 22:33
# @Author : 毛鹏
import ctypes
import os
import string

from playwright._impl._api_types import Error
from playwright.sync_api import sync_playwright, Page, BrowserContext, Browser

from exceptions.error_msg import ERROR_MSG_0039, ERROR_MSG_0040
from exceptions.ui_exception import BrowserPathError
from models.ui_model import WEBConfigModel
from settings.settings import BROWSER_IS_MAXIMIZE


class NewDrowser:

    def __init__(self, web_config: WEBConfigModel):
        self.web_config = web_config
        self.browser_path = ['chrome.exe', 'msedge.exe', 'firefox.exe', '苹果', '360se.exe']

    def new_browser(self) -> Browser:
        playwright = sync_playwright().start()
        if self.web_config.browser_type == 0 or self.web_config.browser_type == 1:
            browser = playwright.chromium
        elif self.web_config.browser_type == 1:
            browser = playwright.firefox
        elif self.web_config.browser_type == 2:
            browser = playwright.webkit
        else:
            raise BrowserPathError(*ERROR_MSG_0039)
        try:
            self.web_config.browser_path = self.web_config.browser_path if self.web_config.browser_path else self.__search_path()
            if BROWSER_IS_MAXIMIZE:
                return browser.launch(headless=self.web_config.is_headless == 1,
                                      executable_path=self.web_config.browser_path,
                                      args=['--start-maximized'])
            else:
                return browser.launch(headless=self.web_config.is_headless == 1,
                                      executable_path=self.web_config.browser_path)
        except Error as error:
            raise BrowserPathError(*ERROR_MSG_0040, error=error)

    def new_context(self, browser: Browser) -> tuple[BrowserContext, Page]:
        context = browser.new_context(no_viewport=True)
        page = context.new_page()
        return context, page

    def __search_path(self, ):
        drives = []
        for letter in string.ascii_uppercase:
            drive = f"{letter}:\\"
            if ctypes.windll.kernel32.GetDriveTypeW(drive) == 3:
                drives.append(drive)
        for i in drives:
            for root, dirs, files in os.walk(i):
                if self.browser_path[self.web_config.browser_type] in files:
                    return os.path.join(root, self.browser_path[self.web_config.browser_type])

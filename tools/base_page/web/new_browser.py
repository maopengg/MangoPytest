# -*- coding: utf-8 -*-
# @Project: MangoActuator
# @Description: 
# @Time   : 2023-04-25 22:33
# @Author : 毛鹏
import asyncio
import ctypes
import os
import string
from typing import Optional

from playwright._impl._api_types import Error
from playwright.async_api import async_playwright, Page, BrowserContext, Browser

from enums.ui_enum import BrowserTypeEnum
from exceptions.error_msg import ERROR_MSG_0039, ERROR_MSG_0040
from exceptions.ui_exception import BrowserPathError
from models.ui_model import WEBConfigModel
from settings.settings import BROWSER_IS_MAXIMIZE
from tools.decorator.singleton import singleton
from tools.log_collector import log


@singleton
class NewBrowser:

    def __init__(self, web_config: WEBConfigModel):
        self.web_config = web_config
        self.browser_path = ['chrome.exe', 'msedge.exe', 'firefox.exe', '苹果', '360se.exe']
        self.browser: Optional[Browser] = None

    async def new_browser(self):
        playwright = await async_playwright().start()
        if self.web_config.browser_type == BrowserTypeEnum.CHROMIUM or self.web_config.browser_type == BrowserTypeEnum.EDGE:
            browser = playwright.chromium
        elif self.web_config.browser_type == BrowserTypeEnum.FIREFOX:
            browser = playwright.firefox
        elif self.web_config.browser_type == BrowserTypeEnum.WEBKIT:
            browser = playwright.webkit
        else:
            raise BrowserPathError(*ERROR_MSG_0039)
        try:
            self.web_config.browser_path = self.web_config.browser_path \
                if self.web_config.browser_path else await self.__search_path()
            if BROWSER_IS_MAXIMIZE:
                self.browser = await browser.launch(headless=self.web_config.is_headless,
                                                    executable_path=self.web_config.browser_path,
                                                    args=['--start-maximized'])
            else:
                self.browser = await browser.launch(headless=self.web_config.is_headless,
                                                    executable_path=self.web_config.browser_path)
        except Error as error:
            raise BrowserPathError(*ERROR_MSG_0040, error=error)

    async def new_context_page(self) -> tuple[BrowserContext, Page]:
        if self.browser is None:
            await self.new_browser()
        context = await self.browser.new_context(no_viewport=True)
        log.warning(str(f'{type(context)}1'))
        return context, await context.new_page()

    async def __search_path(self, ):
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
    asyncio.run(browser.new_context_page())

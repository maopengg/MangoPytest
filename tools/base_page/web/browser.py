# -*- coding: utf-8 -*-
# @Project: MangoActuator
# @Description: 
# @Time   : 2023-04-25 22:33
# @Author : 毛鹏
import time

from playwright.async_api import Locator
from playwright.async_api import Page, BrowserContext

from exceptions.error_msg import ERROR_MSG_0038
from exceptions.ui_exception import UiTimeoutError


class PlaywrightBrowser:
    """浏览器操作"""
    page: Page = None
    context: BrowserContext = None
    url: str = None

    @classmethod
    def w_wait_for_timeout(cls, _time: int):
        """强制等待"""
        time.sleep(int(_time))

    def w_goto(self, url=None):
        """打开URL"""
        try:
            if url:
                self.page.goto(url, timeout=60000)
            else:
                if self.page is None:
                    self.page = self.context.new_page()
                self.page.goto(self.url, timeout=60000)
            time.sleep(2)
        except TimeoutError:
            raise UiTimeoutError(*ERROR_MSG_0038, value=(url if url else self.url,))

    def w_screenshot(self, path: str, full_page=True):
        """整个页面截图"""
        self.page.screenshot(path=path, full_page=full_page)

    @classmethod
    def w_ele_screenshot(cls, locating: Locator, path: str):
        """元素截图"""
        locating.screenshot(path=path)

    def w_alert(self):
        """设置弹窗不予处理"""
        self.page.on("dialog", lambda dialog: dialog.accept())

    def w_download(self, save_path: str):
        """下载文件"""
        with self.page.expect_download() as download_info:
            self.page.get_by_text("Download file").click()
        download = download_info.value
        download.save_as(save_path)

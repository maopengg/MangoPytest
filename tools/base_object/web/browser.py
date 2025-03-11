# -*- coding: utf-8 -*-
# @Project: MangoActuator
# @Description: 
# @Time   : 2023-04-25 22:33
# @Author : 毛鹏
import time

from exceptions import *
from tools.base_object.web.web_object.web_object import WebBaseObject


class PlaywrightBrowser(WebBaseObject):
    """浏览器操作"""

    @classmethod
    def w_wait_for_timeout(cls, _time: int):
        """强制等待"""
        time.sleep(int(_time))

    def w_goto(self, url: str):
        """打开URL"""
        try:
            self.page.goto(url, timeout=60000)
        except TimeoutError:
            raise UiError(*ERROR_MSG_0038, value=(url if url else url,))

    def w_screenshot(self, path: str, full_page=True):
        """整个页面截图"""
        self.page.screenshot(path=path, full_page=full_page)

    def w_ele_screenshot(self, locating: str, path: str):
        """元素截图"""
        self.element(locating).screenshot(path=path)

    def w_alert(self):
        """设置弹窗不予处理"""
        self.page.on("dialog", lambda dialog: dialog.accept())

    def w_download(self, save_path: str):
        """下载文件"""
        with self.page.expect_download() as download_info:
            self.page.get_by_text("Download file").click()
        download = download_info.value
        download.save_as(save_path)

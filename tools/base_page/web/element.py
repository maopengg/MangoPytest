# -*- coding: utf-8 -*-
# @Project: MangoActuator
# @Description: 
# @Time   : 2023-04-26 22:22
# @Author : 毛鹏

import time

from playwright.async_api import Page, BrowserContext, Locator, Error

from exceptions.error_msg import ERROR_MSG_0035
from exceptions.ui_exception import UploadElementInputError


class PlaywrightElement:
    """元素操作"""
    page: Page = None
    context: BrowserContext = None

    @classmethod
    def w_click(cls, locating: Locator):
        """元素点击"""
        locating.click()

    @classmethod
    def w_input(cls, locating: Locator, input_value: str):
        """元素输入"""
        locating.fill(str(input_value))

    def w_get_text(self, locating: Locator, set_cache_key=None):
        """获取元素文本"""
        value = locating.inner_text()
        if set_cache_key:
            self.data_processor.set_cache(key=set_cache_key, value=value)
        return value

    @classmethod
    def w_upload_files(cls, locating: Locator, file_path: str | list):
        """点击元素上传文件"""
        try:
            if isinstance(file_path, str):
                locating.set_input_files(file_path)
            else:
                for file in file_path:
                    locating.set_input_files(file)
        except Error:
            raise UploadElementInputError(*ERROR_MSG_0035)
        # with self.page.expect_file_chooser() as fc_info:
        #     locating.click()
        # file_chooser = fc_info.value
        # file_chooser.set_files(file_path)

    @classmethod
    def w_drag_to(cls, locating1: Locator, locating2: Locator):
        """拖动A元素到达B"""
        locating1.drag_to(locating2)

    @classmethod
    def w_time_click(cls, locating: Locator, _time: int):
        """循环点击指定的时间"""
        s = time.time()
        while True:
            locating.click()
            if time.time() - s > int(_time):
                return

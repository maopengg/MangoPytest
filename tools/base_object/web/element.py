# -*- coding: utf-8 -*-
# @Project: MangoActuator
# @Description: 
# @Time   : 2023-04-26 22:22
# @Author : 毛鹏

import time
from playwright.async_api import Error

from exceptions import *
from tools.base_object.web.web_object.web_object import WebBaseObject


class PlaywrightElement(WebBaseObject):
    """元素操作"""

    def w_click(self, locating: str):
        """元素点击"""
        self.element(locating).click()

    def w_input(self, locating: str, input_value: str):
        """元素输入"""
        self.element(locating).fill(str(input_value))

    def w_get_text(self, locating: str, set_cache_key=None):
        """获取元素文本"""
        value = self.element(locating).inner_text()
        if set_cache_key:
            self.test_data.set_cache(key=set_cache_key, value=value)
        return value

    def w_upload_files(self, locating: str, file_path: str | list):
        """点击元素上传文件"""
        try:
            if isinstance(file_path, str):
                self.element(locating).set_input_files(file_path)
            else:
                for file in file_path:
                    self.element(locating).set_input_files(file)
        except Error:
            raise UiError(*ERROR_MSG_0035)
        # with self.page.expect_file_chooser() as fc_info:
        #     locating.click()
        # file_chooser = fc_info.value
        # file_chooser.set_files(file_path)

    def w_drag_to(self, locating1: str, locating2: str):
        """拖动A元素到达B"""
        self.element(locating1).drag_to(self.element(locating2))

    def w_time_click(self, locating: str, _time: int):
        """循环点击指定的时间"""
        s = time.time()
        while True:
            self.element(locating).click()
            if time.time() - s > int(_time):
                return

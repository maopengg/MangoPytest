# -*- coding: utf-8 -*-
# @Project: MangoActuator
# @Description: 
# @Time   : 2023-04-26 22:22
# @Author : 毛鹏
import time
from typing import Optional

from playwright._impl._api_types import Error
from playwright.sync_api import Locator
from playwright.sync_api import Page, BrowserContext

from exceptions.error_msg import ERROR_MSG_0035, ERROR_MSG_0036
from exceptions.ui_exception import UploadElementInputError, ElementIsEmptyError


class PlaywrightElementOperation:
    """元素操作"""
    page: Page = None
    context: BrowserContext = None

    def w_click(self, locating: Locator):
        """元素点击"""
        locating.click()

    def w_input(self, locating: Locator, input_value: str):
        """元素输入"""
        locating.fill(str(input_value))

    def w_list_input(self, locating: list[Locator], input_list_value: list[str], element_loc: str):
        """DESK定开-列表输入"""

        def find_ele(page) -> Locator:
            return page.locator(f'xpath={element_loc}')

        for loc, data in zip(locating, input_list_value):
            loc.click()
            locator: Optional[Locator] = None
            for i in self.page.frames:
                locator = find_ele(i)
                if locator.count() > 0:
                    break
            if locator is None:
                raise ElementIsEmptyError(*ERROR_MSG_0035)
            locator.fill(str(data))

    def w_get_text(self, locating: Locator, set_cache_key=None):
        """获取元素文本"""
        value = locating.inner_text()
        if set_cache_key:
            self.data_processor.set_cache(key=set_cache_key, value=value)
        return value

    def w_click_right_coordinate(self, locating: Locator):
        """CDP定开-总和坐标点击"""
        button_position = locating.bounding_box()
        # 计算点击位置的坐标
        x = button_position['x'] + button_position['width'] + 50
        y = button_position['y'] - 40
        time.sleep(1)
        self.page.mouse.click(x, y)

    def w_upload_files(self, locating: Locator, file_path: str | list):
        """点击元素上传文件"""
        try:
            if isinstance(file_path, str):
                locating.set_input_files(file_path)
            else:
                for file in file_path:
                    locating.set_input_files(file)
        except Error:
            raise UploadElementInputError(*ERROR_MSG_0036)
        # with self.page.expect_file_chooser() as fc_info:
        #     locating.click()
        # file_chooser = fc_value
        # file_chooser.set_files(file_path)

    def w_drag_to(self, locating1: Locator, locating2: Locator):
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

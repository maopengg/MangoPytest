# -*- coding: utf-8 -*-
# @Project: MangoActuator
# @Description: 
# @Time   : 2023-04-26 22:22
# @Author : 毛鹏
import time
from typing import Optional

from playwright.sync_api import Locator, BrowserContext, Page

from exceptions.error_msg import ERROR_MSG_0022
from exceptions.ui_exception import ElementIsEmptyError


class PlaywrightCustomization:
    """定制开发"""
    page: Page = None
    context: BrowserContext = None

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
                raise ElementIsEmptyError(*ERROR_MSG_0022)
            locator.fill(str(data))

    def w_click_right_coordinate(self, locating: Locator):
        """CDP定开-总和坐标点击"""
        button_position = locating.bounding_box()
        # 计算点击位置的坐标
        x = button_position['x'] + button_position['width'] + 50
        y = button_position['y'] - 40
        time.sleep(1)
        self.page.mouse.click(x, y)

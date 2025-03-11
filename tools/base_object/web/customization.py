# -*- coding: utf-8 -*-
# @Project: MangoActuator
# @Description: 
# @Time   : 2023-04-26 22:22
# @Author : 毛鹏

import time
from playwright.sync_api import Locator

from tools.base_object.web.web_object.web_object import WebBaseObject


class PlaywrightCustomization(WebBaseObject):
    """定制开发"""

    def w_click_right_coordinate(self, locating: Locator):
        """CDP定开-总和坐标点击"""
        button_position = locating.bounding_box()
        # 计算点击位置的坐标
        x = button_position['x'] + button_position['width'] + 50
        y = button_position['y'] - 40
        time.sleep(1)
        self.page.mouse.click(x, y)

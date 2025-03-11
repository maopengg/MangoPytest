# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: # @Time   : 2023-04-29 12:11
# @Author : 毛鹏
import time

from tools.base_object.web.web_object.web_object import WebBaseObject


class PlaywrightDeviceInput(WebBaseObject):
    """输入设备操作"""

    def w_hover(self, locating: str):
        """鼠标悬停"""
        self.element(locating).hover()
        time.sleep(1)

    def w_wheel(self, y):
        """鼠标上下滚动像素，负数代表向上"""
        self.page.mouse.wheel(0, y)

    def w_keys(self, keyboard: str):
        """按键"""
        self.page.keyboard.press(keyboard)

    def w_mouse_center(self):
        """移动鼠标到浏览器中间"""

        viewport_size = self.page.evaluate('''() => {
            return {
                width: window.innerWidth,
                height: window.innerHeight
            }
        }''')
        center_x = viewport_size['width'] / 2
        center_y = viewport_size['height'] / 2
        # 移动鼠标到浏览器中心点
        self.page.mouse.move(center_x, center_y)

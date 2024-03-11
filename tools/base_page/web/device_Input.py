# -*- coding: utf-8 -*-
# @Project: MangoActuator
# @Description: 
# @Time   : 2023-04-29 12:11
# @Author : 毛鹏
import asyncio

from playwright.sync_api import Locator, FrameLocator
from playwright.sync_api import Page, BrowserContext

from enums.ui_enum import ElementExpEnum
from exceptions.error_msg import ERROR_MSG_0042, ERROR_MSG_0043
from exceptions.ui_exception import LocatorError, ElementIsEmptyError
from models.ui_model import ElementModel


class PlaywrightDeviceInput:
    """输入设备操作"""
    page: Page = None
    context: BrowserContext = None

    def w_hover(self, locating: Locator):
        """鼠标悬停"""
        locating.hover()
        asyncio.sleep(1)

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

    def w_find_element(self, element_model: ElementModel) -> Locator:
        """
        基于playwright的元素查找
        @return:
        """

        def find_ele(page: Page, *args, **kwargs) -> Locator:
            is_iframe = False
            if element_model.iframe and is_iframe is False:
                is_iframe = True
                frame_locator: FrameLocator | Page = page
                for loc in element_model.iframe:
                    frame_locator = frame_locator.frame_locator(loc)
                return find_ele(frame_locator)
            elif element_model.method.value == ElementExpEnum.XPATH.value:
                ele = page.locator(f'xpath={element_model.locator}')
            elif element_model.method.value == ElementExpEnum.TEST_ID.value:
                ele = page.get_by_text(*args, **kwargs)
            elif element_model.method.value == ElementExpEnum.PLACEHOLDER.value:
                ele = page.get_by_placeholder(text=element_model.locator, *args, **kwargs)
            elif element_model.method.value == ElementExpEnum.LABEL.value:
                ele = page.get_by_label(*args, **kwargs)
            elif element_model.method.value == ElementExpEnum.TITLE.value:
                ele = page.get_by_title(*args, **kwargs)
            elif element_model.method.value == ElementExpEnum.ROLE.value:
                ele = page.get_by_role(role=element_model.locator, *args, **kwargs)
            elif element_model.method.value == ElementExpEnum.AIT_TEXT.value:
                ele = page.get_by_alt_text(*args, **kwargs)
            elif element_model.method.value == ElementExpEnum.AIT_TEXT.value:
                ele = page.locator(*args, **kwargs)
            else:
                raise LocatorError(*ERROR_MSG_0042)
            ele.filter(has_text=element_model.has_text, has=element_model.has)
            if element_model.locator2:
                ele = page.locator(element_model.locator2).filter(has_text=element_model.has_text,
                                                                  has=element_model.has)
            return ele

        element_dict = {
            'exact': True if element_model.exact else False
        }
        if element_model.name:
            element_dict['name'] = element_model.name

        locator: Locator = find_ele(
            self.page,
            **element_dict
        )
        if locator.count() < 1 or locator is None:
            raise ElementIsEmptyError(*ERROR_MSG_0043, value=(element_model.name, element_model.locator))
        return locator.nth(element_model.nth) if element_model.nth else locator

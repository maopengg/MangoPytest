# -*- coding: utf-8 -*-
# @Project: MangoActuator
# @Description: 
# @Time   : 2023-04-29 12:11
# @Author : 毛鹏
import asyncio

from playwright.sync_api import Locator
from playwright.sync_api import Page, BrowserContext

from enums.tools_enum import StatusEnum
from enums.ui_enum import ElementExpEnum
from exceptions.error_msg import ERROR_MSG_0041, ERROR_MSG_0042, ERROR_MSG_0043
from exceptions.ui_exception import ReplaceElementLocatorError, LocatorError, ElementIsEmptyError


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

    def w_find_element(self, element_model: str) -> Locator | list[Locator]:
        """
        基于playwright的元素查找
        @return:
        """
        if self.data_processor.is_extract(ele_loc):
            element_locator = self.element_model.ope_value.get('element_locator')
            if element_locator:
                ele_loc = self.data_processor.specify_replace(ele_loc, element_locator)
            else:
                raise ReplaceElementLocatorError(*ERROR_MSG_0041)
        self.element_test_result.loc = ele_loc

        def find_ele(page) -> Locator:
            match self.element_model.ele_exp:
                case ElementExpEnum.XPATH.value:
                    ele = page.locator(f'xpath={ele_loc}')
                case ElementExpEnum.TEST_ID.value:
                    ele = page.get_by_test_id(ele_loc)
                case ElementExpEnum.TEXT.value:
                    ele = page.get_by_text(ele_loc, exact=True)
                case ElementExpEnum.PLACEHOLDER.value:
                    ele = page.get_by_placeholder(ele_loc)
                case ElementExpEnum.LABEL.value:
                    ele = page.get_by_label(ele_loc)
                case ElementExpEnum.TITLE.value:
                    ele = page.get_by_title(ele_loc)
                case ElementExpEnum.ROLE.value:
                    ele = page.get_by_role(ele_loc)
                case ElementExpEnum.AIT_TEXT.value:
                    ele = page.get_by_alt_text(ele_loc)
                case _:
                    raise LocatorError(*ERROR_MSG_0042)
            if self.element_model.locator:
                ele = ele.locator(self.element_model.locator)
            return ele

        if self.element_model.is_iframe == StatusEnum.SUCCESS.value:
            ele_list: list[Locator] = []
            for i in self.page.frames:
                locator: Locator = find_ele(i)
                count = locator.count()
                if count > 0:
                    for nth in range(0, count):
                        ele_list.append(locator.nth(nth))
            self.element_test_result.ele_quantity = len(ele_list)
            if len(ele_list) < 1:
                if self.element_model.type == 0:
                    raise ElementIsEmptyError(*ERROR_MSG_0043, value=(self.element_model.ele_name_a, ele_loc))
            else:
                if self.element_model.ele_sub == 10000:
                    return ele_list
            return ele_list[self.element_model.ele_sub - 1] if self.element_model.ele_sub else ele_list[0]
        else:
            locator: Locator = find_ele(self.page)
            count = locator.count()
            self.element_test_result.ele_quantity = count
            if count < 1 or locator is None:
                if self.element_model.type == 0:
                    raise ElementIsEmptyError(*ERROR_MSG_0043, value=(self.element_model.ele_name_a, ele_loc))
            else:
                if self.element_model.ele_sub == 10000:
                    return [locator.nth(i) for i in range(0, count)]

            if self.element_model.ele_sub is None:
                return locator
            else:
                return locator.nth(self.element_model.ele_sub - 1)

# -*- coding: utf-8 -*-
# @Project: MangoActuator
# @Description: 
# @Time   : 2023-07-15 11:57
# @Author : 毛鹏
import json
import re

import allure
from playwright.async_api import Locator
from playwright.async_api import Page, BrowserContext
from retrying import retry

from exceptions.error_msg import ERROR_MSG_0043, ERROR_MSG_0344, ERROR_MSG_0346
from exceptions.ui_exception import ElementIsEmptyError, UiElementLocatorError, UiElementIsNullError
from sources import SourcesData
from tools.base_page.web import WebDevice
from tools.data_processor import DataProcessor


class BasePage(WebDevice):

    def __init__(self, project_id: int,
                 module_name: str,
                 context_page: tuple[BrowserContext, Page],
                 data_processor: DataProcessor):
        context, page = context_page
        super().__init__(page, context, data_processor)
        self.element_list: list[dict] = SourcesData.ui_element[
            (SourcesData.ui_element['project_id'] == project_id) & (
                    SourcesData.ui_element['module_name'] == module_name)].to_dict(orient='records')
        if not self.element_list:
            raise UiElementIsNullError(*ERROR_MSG_0346)
        d = re.DEBUG

    @retry(stop_max_attempt_number=5, wait_fixed=1000)
    async def element(self, ele_name: str, is_ope: bool = True) -> Locator:
        for element in self.element_list:
            if element.get('ele_name') == ele_name:
                try:
                    locator: Locator = eval(f"await self.{element.get('locator')}")
                except SyntaxError:
                    raise UiElementLocatorError(*ERROR_MSG_0344)
                allure.attach(json.dumps(element, ensure_ascii=False), ele_name)
                # allure.attach(self.page.screenshot(full_page=True), name="失败截图", attachment_type=allure.attachment_type.PNG)
                if is_ope:
                    if await locator.count() < 1 or locator is None:
                        raise ElementIsEmptyError(*ERROR_MSG_0043,
                                                  value=(element.get('ele_name'), element.get('locator')))
                    return locator.nth(element.get('nth')) if element.get('nth') else locator
                else:
                    return locator

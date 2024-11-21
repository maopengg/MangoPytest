# -*- coding: utf-8 -*-
# @Project: 芒果测试平台# @Description:
# @Time   : 2023-07-15 11:57
# @Author : 毛鹏
import json
import re

import allure
from playwright.sync_api import Locator
from playwright.sync_api import Page, BrowserContext
from retrying import retry

from enums.ui_enum import ElementExpEnum
from exceptions import *
from sources import SourcesData
from tools.base_page.web import WebDevice
from tools.obtain_test_data import ObtainTestData


class BasePage(WebDevice):

    def __init__(self, project_name: str,
                 module_name: str,
                 context_page: tuple[BrowserContext, Page],
                 test_data: ObtainTestData):
        context, page = context_page
        super().__init__(page, context, test_data)
        self.element_list: list[dict] = SourcesData.ui_element[
            (SourcesData.ui_element['project_name'] == project_name) & (
                    SourcesData.ui_element['module_name'] == module_name)].to_dict(orient='records')
        if not self.element_list:
            raise UiError(*ERROR_MSG_0346)
        d = re.DEBUG

    @retry(stop_max_attempt_number=5, wait_fixed=1000)
    def element(self, ele_name: str, is_ope: bool = True) -> Locator:
        for element in self.element_list:
            if element.get('ele_name') == ele_name:
                try:
                    if element.get('method') == ElementExpEnum.LOCATOR.value:
                        locator: Locator = eval(f"self.page.{element.get('locator')}")
                    elif element.get('method') == ElementExpEnum.XPATH.value:
                        ele = element.get('locator')
                        locator: Locator = self.page.locator(f'xpath={ele}')
                    else:
                        raise UiError(300, '还未支持这个元素定位方式')
                except SyntaxError:
                    raise UiError(*ERROR_MSG_0344)
                allure.attach(json.dumps(element, ensure_ascii=False), ele_name)
                # allure.attach(self.page.screenshot(full_page=True), name="失败截图", attachment_type=allure.attachment_type.PNG)
                if is_ope:
                    if locator.count() < 1 or locator is None:
                        raise UiError(*ERROR_MSG_0043,
                                      value=(element.get('ele_name'), element.get('locator')))
                    return locator.nth(element.get('nth')) if element.get('nth') else locator
                else:
                    return locator

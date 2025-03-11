# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2025-03-11 14:47
# @Author : 毛鹏
import json
import re

import allure
from playwright.async_api import Locator
from playwright.async_api import Page, BrowserContext
from playwright.sync_api import Locator
from retrying import retry

from enums.ui_enum import ElementExpEnum
from exceptions import *
from exceptions import UiError
from sources import SourcesData
from tools.obtain_test_data import ObtainTestData


class WebBaseObject:

    def __init__(self,
                 project_name: str,
                 page_name: str,
                 module_name: str,
                 context_page: tuple[BrowserContext, Page],
                 test_data: ObtainTestData,
                 ):
        self.context, self.page = context_page
        self.test_data = test_data
        self.project_name = project_name
        self.module_name = module_name
        self.page_name = page_name

        d = re.DEBUG

    def setup(self) -> None:
        self.page = None
        self.context = None

    def base_close(self):
        if self.context and isinstance(self.context, BrowserContext):
            self.context.close()
        if self.page and isinstance(self.page, Page):
            self.page.close()
        self.setup()

    @retry(stop_max_delay=10000, wait_fixed=100)
    def element(self, ele_name: str) -> Locator:
        element_dict: dict = SourcesData.get_ui_element(
            project_name=self.project_name,
            module_name=self.module_name,
            page_name=self.page_name,
            ele_name=ele_name,
        )
        element_dict['locator'] = self.test_data.replace_str(element_dict.get('locator'))
        if not element_dict:
            raise UiError(*ERROR_MSG_0346)
        try:
            if element_dict.get('method') == ElementExpEnum.LOCATOR.value:
                locator: Locator = eval(f"self.page.{element_dict.get('locator')}")
            elif element_dict.get('method') == ElementExpEnum.XPATH.value:
                ele = element_dict.get('locator')
                locator: Locator = self.page.locator(f'xpath={ele}')
            else:
                raise UiError(300, '还未支持这个元素定位方式')
        except SyntaxError:
            raise UiError(*ERROR_MSG_0344)
        allure.attach(json.dumps(element_dict, ensure_ascii=False), ele_name)
        allure.attach(self.page.screenshot(full_page=True), name="失败截图",
                      attachment_type=allure.attachment_type.PNG)
        if locator.count() < 1 or locator is None:
            raise UiError(*ERROR_MSG_0043, value=(element_dict.get('ele_name'), element_dict.get('locator')))
        return locator.nth(element_dict.get('nth')) if element_dict.get('nth') else locator

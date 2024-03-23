# -*- coding: utf-8 -*-
# @Project: MangoActuator
# @Description: 
# @Time   : 2023-07-15 11:57
# @Author : 毛鹏
import re

from playwright.sync_api import Locator
from playwright.sync_api import Page, BrowserContext

from exceptions.error_msg import ERROR_MSG_0043, ERROR_MSG_0344
from exceptions.ui_exception import ElementIsEmptyError, UiElementLocatorError
from tools.base_page.web import WebDevice
from tools.data_processor import DataProcessor
from tools.database.sql_statement import sql_statement_1
from tools.database.sqlite_connect import SQLiteConnect


class BasePage(WebDevice):

    def __init__(self, project_id: int,
                 module_name: str,
                 context_page: tuple[BrowserContext, Page],
                 data_processor: DataProcessor):
        context, page = context_page
        super().__init__(page, context, data_processor)
        self.element_list: list[dict] = SQLiteConnect().execute_sql(sql_statement_1, (project_id, module_name))

    def element(self, ele_name: str, is_ope: bool = True) -> Locator:
        for element in self.element_list:
            if element.get('ele_name') == ele_name:
                try:
                    locator: Locator = eval(f"self.{element.get('locator')}")
                except SyntaxError:
                    raise UiElementLocatorError(*ERROR_MSG_0344)
                if is_ope:
                    if locator.count() < 1 or locator is None:
                        raise ElementIsEmptyError(*ERROR_MSG_0043,
                                                  value=(element.get('ele_name'), element.get('locator')))
                    return locator.nth(element.get('nth')) if element.get('nth') else locator
                else:
                    return locator

# -*- coding: utf-8 -*-
# @Project: MangoActuator
# @Description: 
# @Time   : 2023-07-15 11:57
# @Author : 毛鹏
from playwright.sync_api import Page, BrowserContext

from models.ui_model import ElementModel
from tools.base_page.web import WebDevice
from tools.data_processor import DataProcessor
from tools.database.sqlite_handler import SQLiteHandler


class BasePage(WebDevice):

    def __init__(self, context_page: tuple[BrowserContext, Page], data_processor: DataProcessor):
        context, page = context_page
        super().__init__(page, context, data_processor)
        self.element_list = SQLiteHandler().execute_sql('select * from ui_element where project_id=3')

    def element_model(self, ele_name: str) -> ElementModel:
        for i in self.element_list:
            if i.get('ele_name') == ele_name:
                return ElementModel(**i)

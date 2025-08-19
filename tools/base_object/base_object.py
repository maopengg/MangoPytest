# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2025-04-21 15:09
# @Author : 毛鹏
import re

from mangoautomation.enums import ElementOperationEnum
from mangoautomation.uidrive import BaseData
from mangoautomation.uidrive.web.sync_web import SyncWebDevice
from mangotools.decorator import sync_retry
from mangotools.enums import StatusEnum
from playwright.async_api import Page, BrowserContext
from playwright.sync_api import Locator

from sources import SourcesData
from tools import project_dir
from tools.log import log
from tools.obtain_test_data import ObtainTestData


class WebBaseObject(SyncWebDevice):

    def __init__(self,
                 project_name: str,
                 module_name: str,
                 page_name: str,
                 context_page: tuple[BrowserContext, Page],
                 test_data: ObtainTestData,
                 ):
        self.context, self.page = context_page
        self.test_data = test_data
        self.project_name = project_name
        self.module_name = module_name
        self.page_name = page_name
        self.base_data = BaseData(self.test_data, log)
        self.base_data.set_file_path(project_dir.download(), project_dir.screenshot())
        self.base_data.set_page_context(self.page, self.context)
        super().__init__(self.base_data)
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

    @sync_retry()
    def element(self, ele_name: str) -> Locator:
        element_dict: dict = SourcesData.get_ui_element(
            project_name=self.project_name,
            module_name=self.module_name,
            page_name=self.page_name,
            ele_name=ele_name,
        )
        element_dict['locator'] = self.test_data.replace(element_dict.get('locator'))
        loc, count, text = self.web_find_ele(
            element_dict.get('ele_name'),
            ElementOperationEnum.OPE.value,
            element_dict.get('method'),
            element_dict.get('locator'),
            element_dict.get('nth'),
            StatusEnum.FAIL.value,
        )
        return loc
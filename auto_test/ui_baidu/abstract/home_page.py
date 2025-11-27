# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-04-01 16:04
# @Author : 毛鹏
from urllib.parse import urljoin

from playwright.sync_api import Page, BrowserContext
from mangoautomation.uidrive import BaseData

from auto_test.project_config import ProjectEnum
from models.tools_model import BaseDataModel
from tools import project_dir
from tools.base_object.base_object import WebBaseObject
from tools.obtain_test_data import ObtainTestData

from tools.log import log


class HomePage(WebBaseObject):
    """
    百度首页
    """

    def __init__(self,
                 base_data: BaseData,
                 base_data_model: BaseDataModel,
                 test_data: ObtainTestData):
        project_name = ProjectEnum.BAIDU.value
        module_name = '首页'
        page_name = '首页'
        self.base_data_model = base_data_model
        self.base_data = base_data
        self.test_data = test_data
        super().__init__(project_name, module_name, page_name, self.base_data, test_data)
        self.url = urljoin(base_data_model.test_object.host, '')

    def goto(self):
        self.w_goto(self.url)

    def search_keyword(self, keyword: str):
        self.w_input(self.element('搜索框'), keyword)
        self.w_wait_for_timeout(2)
        self.w_force_click(self.element('百度一下'))

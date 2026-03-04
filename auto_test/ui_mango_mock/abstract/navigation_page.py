# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2026-03-04 14:15
# @Author : 毛鹏
from urllib.parse import urljoin

from mangoautomation.uidrive import BaseData

from auto_test.project_config import ProjectEnum
from models.tools_model import BaseDataModel
from tools.base_object.base_object import WebBaseObject
from tools.obtain_test_data import ObtainTestData


class NavigationPage(WebBaseObject):
    """
    页面导航页面
    """

    def __init__(self,
                 base_data: BaseData,
                 base_data_model: BaseDataModel,
                 test_data: ObtainTestData):
        project_name = ProjectEnum.MOCK_UI.value
        module_name = '页面导航'
        page_name = '页面导航页面'
        self.base_data_model = base_data_model
        self.base_data = base_data
        self.test_data = test_data
        super().__init__(project_name, module_name, page_name, self.base_data, test_data)
        self.url = urljoin(base_data_model.test_object.host, '')

    def goto(self):
        self.base_data.page.goto(self.url, timeout=30000)

    def test_navigation(self):
        """测试页面导航"""
        self.w_open_new_tab_and_switch(self.element('打开新标签页'))
        self.w_wait_for_timeout(2)
        self.w_switch_tabs(1)
        text = self.w_get_text(self.element('新页面元素'))
        self.w_switch_tabs(0)
        return text


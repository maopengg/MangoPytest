# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2026-03-04 14:15
# @Author : 毛鹏
from urllib.parse import urljoin

from mangoautomation.uidrives import BaseData

from auto_tests.project_registry import ProjectEnum
from auto_tests.ui.simple_ui.config import settings
from core.ui import WebBaseObject
from core.utils.obtain_test_data  import ObtainTestData


class ScrollPage(WebBaseObject):
    """
    滚动页面
    """

    def __init__(self,
                 base_data: BaseData,
                 test_data: ObtainTestData):
        project_name = ProjectEnum.SIMPLE_UI.value
        module_name = '滚动像素'
        page_name = '滚动页面'
        self.base_data = base_data
        self.test_data = test_data
        super().__init__(project_name, module_name, page_name, self.base_data, test_data, settings)
        self.url = settings.BASE_URL

    def goto(self):
        self.base_data.page.goto(self.url, timeout=30000)

    def test_scroll(self):
        """测试页面滚动"""
        self.element_action('内容行 10', 'w_element_wheel')
        self.w_wait_for_timeout(1)
        self.element_action('底部内容', 'w_element_wheel')
        self.w_wait_for_timeout(1)
        return self.element_action('底部内容', 'w_get_text')

# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2026-03-04 14:15
# @Author : 毛鹏
from urllib.parse import urljoin

from mangoautomation.uidrive import BaseData

from auto_tests.pytest_ui_mock import PROJECT_DISPLAY_NAME
from auto_tests.pytest_ui_mock.config import settings
from core.ui import WebBaseObject
from core.utils.obtain_test_data  import ObtainTestData


class FlashPage(WebBaseObject):
    """
    闪现元素页面
    """

    def __init__(self,
                 base_data: BaseData,
                 test_data: ObtainTestData):
        project_name = PROJECT_DISPLAY_NAME
        module_name = '闪现元素'
        page_name = '闪现元素页面'
        self.base_data = base_data
        self.test_data = test_data
        super().__init__(project_name, module_name, page_name, self.base_data, test_data)
        self.url = urljoin(settings.BASE_URL, "/")

    def goto(self):
        self.base_data.page.goto(self.url, timeout=30000)

    def test_flash_element(self):
        """捕获闪现元素"""
        self.w_click(self.element('显示闪现元素'))
        self.w_wait_for_timeout(0.5)
        return self.w_get_text(self.element('结果'))

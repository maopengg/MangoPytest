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


class InputPage(WebBaseObject):
    """
    输入框页面
    """

    def __init__(self,
                 base_data: BaseData,
                 test_data: ObtainTestData):
        project_name = PROJECT_DISPLAY_NAME
        module_name = '输入框'
        page_name = '输入框页面'
        self.base_data = base_data
        self.test_data = test_data
        super().__init__(project_name, module_name, page_name, self.base_data, test_data)
        self.url = urljoin(settings.BASE_URL, "/")

    def goto(self):
        self.base_data.page.goto(self.url, timeout=30000)

    def test_input_types(self, value: str):
        """测试不同类型的输入"""
        # 普通输入框
        self.w_input(self.element('普通输入框'), value)
        # 数字输入框
        self.w_input(self.element('数字输入框'), '123')
        # 密码输入框
        self.w_input(self.element('密码输入框'), 'password123')
        self.w_wait_for_timeout(1)
        return self.w_get_text(self.element('结果'))

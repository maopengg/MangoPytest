# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2026-03-04 14:15
# @Author : 毛鹏
from urllib.parse import urljoin

from mangoautomation.uidrive import BaseData

from auto_tests.project_config import ProjectEnum
from models.tools_model import BaseDataModel
from tools.base_object.base_object import WebBaseObject
from tools.obtain_test_data import ObtainTestData


class BatchPage(WebBaseObject):
    """
    批量操作页面
    """

    def __init__(self,
                 base_data: BaseData,
                 base_data_model: BaseDataModel,
                 test_data: ObtainTestData):
        project_name = ProjectEnum.MOCK_UI.value
        module_name = '批量操作'
        page_name = '批量操作'
        self.base_data_model = base_data_model
        self.base_data = base_data
        self.test_data = test_data
        super().__init__(project_name, module_name, page_name, self.base_data, test_data)
        self.url = urljoin(base_data_model.test_object.host, '')

    def goto(self):
        self.base_data.page.goto(self.url, timeout=30000)

    def test_batch_checkbox(self):
        """批量勾选复选框"""
        checkboxes = self.element('复选框')
        self.w_many_click(checkboxes)
        self.w_wait_for_timeout(1)
        return self.w_get_text(self.element('结果'))

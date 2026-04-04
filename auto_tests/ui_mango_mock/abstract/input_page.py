# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2026-03-04 14:15
# @Author : 毛鹏
from urllib.parse import urljoin

from mangoautomation.uidrive import BaseData

from auto_tests.project_config import ProjectEnum
from core.models.tools_model import BaseDataModel
from core.base import WebBaseObject
from core.utils.obtain_test_data  import ObtainTestData


class InputPage(WebBaseObject):
    """
    输入框页面
    """

    def __init__(self,
                 base_data: BaseData,
                 base_data_model: BaseDataModel,
                 test_data: ObtainTestData):
        project_name = ProjectEnum.MOCK_UI.value
        module_name = '输入框'
        page_name = '输入框页面'
        self.base_data_model = base_data_model
        self.base_data = base_data
        self.test_data = test_data
        super().__init__(project_name, module_name, page_name, self.base_data, test_data)
        self.url = urljoin(base_data_model.test_object.host, '')

    def goto(self):
        self.base_data.page.goto(self.url, timeout=30000)

    def test_input_types(self, value: str):
        """测试不同类型的输入框"""
        self.w_input(self.element('普通文本输入框'), value)
        self.w_input(self.element('密码输入框'), value)
        self.w_input(self.element('邮箱输入框'), f'{value}@test.com')
        self.w_input(self.element('数字输入框'), '123')
        self.w_input(self.element('多行文本输入框'), value)
        self.w_wait_for_timeout(1)
        return self.w_get_text(self.element('结果'))

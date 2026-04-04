# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2025-11-27 11:51
# @Author : 毛鹏

from urllib.parse import urljoin

from mangoautomation.uidrives import BaseData

from auto_tests.project_config import ProjectEnum
from core.models.tools_model import BaseDataModel
from core.base import WebBaseObject
from core.utils.obtain_test_data  import ObtainTestData


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
        super().__init__(project_name, module_name, page_name, base_data, test_data)
        self.url = urljoin(base_data.test_object.host, '')

    def goto(self):
        self.w_goto(self.url)

    def click_open_source(self):
        self.w_click(self.element('菜单-开源'))

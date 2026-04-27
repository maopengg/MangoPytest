# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2025-11-27 11:51
# @Author : 毛鹏

from urllib.parse import urljoin

from mangoautomation.uidrive import BaseData

from auto_tests.project_config import ProjectEnum
from auto_tests.ui_baidu.config import settings
from core.ui import WebBaseObject
from core.utils.obtain_test_data  import ObtainTestData


class ImgPage(WebBaseObject):
    """
    百度图片页面
    """

    def __init__(self,
                 base_data: BaseData,
                 test_data: ObtainTestData):
        project_name = ProjectEnum.BAIDU.value
        module_name = '图片'
        page_name = '图片页面'
        super().__init__(project_name, module_name, page_name, base_data, test_data)
        self.url = settings.BASE_URL

    def goto(self):
        self.w_goto(self.url)

    def click_open_source(self):
        self.w_click(self.element('菜单-开源'))

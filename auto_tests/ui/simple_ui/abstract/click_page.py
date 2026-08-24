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
from core.utils.obtain_test_data import ObtainTestData


class ClickPage(WebBaseObject):
    """
    元素点击页面
    """

    def __init__(self,
                 base_data: BaseData,
                 test_data: ObtainTestData):
        project_name = ProjectEnum.SIMPLE_UI.value
        module_name = '元素点击'
        page_name = '元素点击'
        self.base_data = base_data
        self.test_data = test_data
        super().__init__(project_name, module_name, page_name, self.base_data, test_data, settings)
        self.url = settings.BASE_URL

    def goto(self):
        self.base_data.page.goto(self.url, timeout=30000)

    def test_double_click(self):
        """双击操作"""
        self.element_action('双击按钮', 'w_dblclick')
        return self.element_action('结果', 'w_get_text')

    def test_right_click(self):
        """右键点击操作"""
        self.element_action('右键点击按钮', 'w_right_click')
        return self.element_action('结果', 'w_get_text')

    def test_force_click(self):
        """强制点击操作"""
        self.element_action('强制点击按钮', 'w_force_click')
        return self.element_action('结果', 'w_get_text')

    def test_simple_click(self):
        """简单点击操作"""
        self.element_action('简单点击按钮', 'w_click')
        return self.element_action('结果', 'w_get_text')

    def test_hover(self):
        """鼠标悬停操作"""
        self.element_action('鼠标悬停按钮', 'w_hover')
        return self.element_action('结果', 'w_get_text')

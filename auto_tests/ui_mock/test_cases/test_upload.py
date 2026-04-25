# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2026-03-04 14:15
# @Author : 毛鹏

import os

import allure

from auto_tests.ui_mock.abstract.home_page import HomePage
from auto_tests.ui_mock.abstract.upload_page import UploadPage
from core.utils.obtain_test_data import ObtainTestData


@allure.epic('演示-UI自动化-WEB项目-MockUI服务')
class TestUpload:
    test_data: ObtainTestData = ObtainTestData()

    @allure.title('演示-文件上传')
    def test_01(self, base_data):
        """ID: 8 - 演示-文件上传"""
        data = {"value": "文件上传测试"}
        self.test_data.set_cache('菜单名称', data.get('value'))
        home_page = HomePage(base_data, self.test_data)
        home_page.goto()
        home_page.switch_menu()
        upload_page = UploadPage(base_data, self.test_data)

        # 使用项目中的测试文件
        file_path = os.path.join(os.path.dirname(__file__), '../../upload/测试上传文件UI.xlsx')
        result = upload_page.test_upload_file(file_path)
        assert result is not None

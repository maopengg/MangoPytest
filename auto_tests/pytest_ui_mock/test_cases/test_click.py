# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2026-03-04 14:15
# @Author : 毛鹏

import allure

from auto_tests.pytest_ui_mock.page_object.click_page import ClickPage
from auto_tests.pytest_ui_mock.page_object.home_page import HomePage
from core.utils.obtain_test_data import ObtainTestData


@allure.epic('演示-UI自动化-WEB项目-MockUI服务')
class TestClick:
    test_data: ObtainTestData = ObtainTestData()

    @allure.title('演示-元素点击操作')
    def test_01(self, base_data):
        """ID: 3 - 演示-元素点击操作"""
        home_page = HomePage(base_data, self.test_data)
        home_page.goto()
        click_page = ClickPage(base_data, self.test_data)

        # 测试双击
        result = click_page.test_double_click()
        assert result is not None

        # 测试右键点击
        result = click_page.test_right_click()
        assert result is not None

        # 测试强制点击
        result = click_page.test_force_click()
        assert result is not None

        # 测试简单点击
        result = click_page.test_simple_click()
        assert result is not None

        # 测试鼠标悬停
        result = click_page.test_hover()
        assert result is not None

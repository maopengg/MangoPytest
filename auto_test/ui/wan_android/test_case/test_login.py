# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2024-02-20 11:11
# @Author : 毛鹏
import time

import allure
import pytest
from playwright.sync_api import sync_playwright


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        yield browser
        browser.close()


@allure.feature("百度搜索")
class TestLogin:

    def test_example(self, browser):
        page = browser.new_page()
        page.goto("https://example.com")
        title = page.title()
        assert "Example Domain" in title


if __name__ == '__main__':
    pytest.main(
        [r'D:\GitCode\PytestAutoTest\auto_test\ui\wan_android\test_case\test_login.py::TestLogin::test_example'])

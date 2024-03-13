# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2024-03-13 11:44
# @Author : 毛鹏
import re
import time

from playwright.sync_api import sync_playwright

code_snippets = {
    "filter": 'page.locator("li").filter(has_text=re.compile(r"^登录$"))',
    "username": 'page.get_by_role("textbox", name="请输入用户名")',
    "password": 'page.get_by_role("textbox", name="请输入密码")',
    "login_button": 'page.locator("#loginDialog div").get_by_text("登录")'
}

# 通过键值对的方式取出值
filter_code = code_snippets["filter"]
username_code = code_snippets["username"]
password_code = code_snippets["password"]
login_button_code = code_snippets["login_button"]


def test_example() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False,
                                    executable_path=r'C:\Users\Administrator\AppData\Local\Google\Chrome\Application\chrome.exe')
        page = browser.new_page()

        page.goto('https://wanandroid.com/index')
        eval(filter_code).click()
        eval(username_code).fill("maopeng")
        eval(password_code).fill("729164035")
        eval(login_button_code).click()
        time.sleep(10)


if __name__ == '__main__':
    test_example()

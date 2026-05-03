# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 键盘操作 BDD 步骤定义
# @Time   : 2026-05-03
# @Author : 毛鹏
from pytest_bdd import when, then

from auto_tests.bdd_ui_mock.page_object.home_page import HomePage
from auto_tests.bdd_ui_mock.page_object.keyboard_page import KeyboardPage


@when("用户进入键盘操作页面")
def user_enter_keyboard_page(logged_in_user, page_context):
    home = page_context.get("首页")
    if not home:
        home = HomePage(logged_in_user["base_data"], logged_in_user["base_data"].test_data)
        home.goto()
        page_context["首页"] = home
    home.switch_menu()
    keyboard_page = KeyboardPage(logged_in_user["base_data"], logged_in_user["base_data"].test_data)
    page_context["键盘"] = keyboard_page


@when("用户执行键盘输入操作")
def user_perform_keyboard_input(logged_in_user, page_context, test_data_context):
    keyboard_page = page_context["键盘"]
    result = keyboard_page.test_keyboard_input()
    test_data_context["键盘结果"] = result


@then("键盘操作应该成功")
def verify_keyboard_success(test_data_context):
    assert test_data_context.get("键盘结果") is not None, "键盘操作失败"

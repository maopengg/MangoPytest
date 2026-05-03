# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 鼠标操作 BDD 步骤定义
# @Time   : 2026-05-03
# @Author : 毛鹏
from pytest_bdd import when, then

from auto_tests.bdd_ui_mock.page_object.home_page import HomePage
from auto_tests.bdd_ui_mock.page_object.mouse_page import MousePage


@when("用户进入鼠标操作页面")
def user_enter_mouse_page(logged_in_user, page_context):
    home = page_context.get("首页")
    if not home:
        home = HomePage(logged_in_user["base_data"], logged_in_user["base_data"].test_data)
        home.goto()
        page_context["首页"] = home
    home.switch_menu()
    mouse_page = MousePage(logged_in_user["base_data"], logged_in_user["base_data"].test_data)
    page_context["鼠标"] = mouse_page


@when("用户执行鼠标悬停操作")
def user_perform_mouse_hover(logged_in_user, page_context, test_data_context):
    mouse_page = page_context["鼠标"]
    result = mouse_page.test_mouse_operations()
    test_data_context["鼠标结果"] = result


@then("鼠标操作应该成功")
def verify_mouse_success(test_data_context):
    assert test_data_context.get("鼠标结果") is not None, "鼠标操作失败"

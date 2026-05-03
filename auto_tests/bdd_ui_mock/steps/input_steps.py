# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 输入框 BDD 步骤定义
# @Time   : 2026-05-03
# @Author : 毛鹏
from pytest_bdd import when, then, parsers

from auto_tests.bdd_ui_mock.page_object.home_page import HomePage
from auto_tests.bdd_ui_mock.page_object.input_page import InputPage


@when("用户进入输入框页面")
def user_enter_input_page(logged_in_user, page_context):
    home = page_context.get("首页")
    if not home:
        home = HomePage(logged_in_user["base_data"], logged_in_user["base_data"].test_data)
        home.goto()
        page_context["首页"] = home
    home.test_data.set_cache('菜单名称', '输入框测试')
    home.switch_menu()
    input_page = InputPage(logged_in_user["base_data"], logged_in_user["base_data"].test_data)
    page_context["输入"] = input_page


@when(parsers.cfparse("用户输入测试值 {value}"))
def user_input_test_value(logged_in_user, page_context, test_data_context, value: str):
    input_page = page_context["输入"]
    result = input_page.test_input_types(value)
    test_data_context["输入结果"] = result


@then("输入操作应该成功")
def verify_input_success(test_data_context):
    assert test_data_context.get("输入结果") is not None, "输入操作失败"

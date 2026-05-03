# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 元素点击 BDD 步骤定义
# @Time   : 2026-05-03
# @Author : 毛鹏
from pytest_bdd import when, then

from auto_tests.bdd_ui_mock.page_object.home import HomePage
from auto_tests.bdd_ui_mock.page_object.click import ClickPage


@when("用户进入元素点击页面")
def user_enter_click(logged_in_user, page_context):
    home = page_context.get("首页")
    if not home:
        home = HomePage(logged_in_user["base_data"], logged_in_user["base_data"].test_data)
        home.goto()
        page_context["首页"] = home
    click = ClickPage(logged_in_user["base_data"], logged_in_user["base_data"].test_data)
    page_context["点击"] = click


@when("用户执行双击操作")
def user_perform_double_click(logged_in_user, page_context, test_data_context):
    click = page_context["点击"]
    result = click.test_double_click()
    test_data_context["双击结果"] = result


@when("用户执行右键点击操作")
def user_perform_right_click(logged_in_user, page_context, test_data_context):
    click = page_context["点击"]
    result = click.test_right_click()
    test_data_context["右键结果"] = result


@when("用户执行强制点击操作")
def user_perform_force_click(logged_in_user, page_context, test_data_context):
    click = page_context["点击"]
    result = click.test_force_click()
    test_data_context["强制点击结果"] = result


@when("用户执行普通点击操作")
def user_perform_simple_click(logged_in_user, page_context, test_data_context):
    click = page_context["点击"]
    result = click.test_simple_click()
    test_data_context["普通点击结果"] = result


@when("用户执行悬停操作")
def user_perform_hover(logged_in_user, page_context, test_data_context):
    click = page_context["点击"]
    result = click.test_hover()
    test_data_context["悬停结果"] = result


@then("双击操作应该成功")
def verify_double_click_success(test_data_context):
    assert test_data_context.get("双击结果") is not None, "双击操作失败"


@then("右键点击操作应该成功")
def verify_right_click_success(test_data_context):
    assert test_data_context.get("右键结果") is not None, "右键点击操作失败"


@then("强制点击操作应该成功")
def verify_force_click_success(test_data_context):
    assert test_data_context.get("强制点击结果") is not None, "强制点击操作失败"


@then("普通点击操作应该成功")
def verify_simple_click_success(test_data_context):
    assert test_data_context.get("普通点击结果") is not None, "普通点击操作失败"


@then("悬停操作应该成功")
def verify_hover_success(test_data_context):
    assert test_data_context.get("悬停结果") is not None, "悬停操作失败"

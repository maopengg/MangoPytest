# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 浏览器弹窗 BDD 步骤定义
# @Time   : 2026-05-03
# @Author : 毛鹏
from pytest_bdd import when, then

from auto_tests.bdd_ui_mock.page_object.home_page import HomePage
from auto_tests.bdd_ui_mock.page_object.alert_page import AlertPage


@when("用户进入浏览器弹窗页面")
def user_enter_alert_page(logged_in_user, page_context):
    home = page_context.get("首页")
    if not home:
        home = HomePage(logged_in_user["base_data"], logged_in_user["base_data"].test_data)
        home.goto()
        page_context["首页"] = home
    home.switch_menu()
    alert_page = AlertPage(logged_in_user["base_data"], logged_in_user["base_data"].test_data)
    page_context["弹窗"] = alert_page


@when("用户触发 alert 弹窗")
def user_trigger_alert(logged_in_user, page_context):
    page_context["弹窗"].test_alert()


@when("用户触发 confirm 弹窗")
def user_trigger_confirm(logged_in_user, page_context):
    page_context["弹窗"].test_confirm()


@when("用户触发 prompt 弹窗")
def user_trigger_prompt(logged_in_user, page_context):
    page_context["弹窗"].test_prompt()


@then("浏览器弹窗操作应该成功")
def verify_alert_success():
    pass

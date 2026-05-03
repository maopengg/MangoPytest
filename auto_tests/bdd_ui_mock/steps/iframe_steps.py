# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: iframe BDD 步骤定义
# @Time   : 2026-05-03
# @Author : 毛鹏
from pytest_bdd import when, then

from auto_tests.bdd_ui_mock.page_object.home import HomePage
from auto_tests.bdd_ui_mock.page_object.iframe import IframePage


@when("用户进入 iframe 页面")
def user_enter_iframe(logged_in_user, page_context):
    home = page_context.get("首页")
    if not home:
        home = HomePage(logged_in_user["base_data"], logged_in_user["base_data"].test_data)
        home.goto()
        page_context["首页"] = home
    home.test_data.set_cache('菜单名称', 'iframe嵌套测试')
    home.switch_menu()
    iframe = IframePage(logged_in_user["base_data"], logged_in_user["base_data"].test_data)
    page_context["iframe"] = iframe


@when("用户操作 iframe 中元素")
def user_operate_iframe_element(logged_in_user, page_context, test_data_context):
    iframe = page_context["iframe"]
    result = iframe.test_iframe_element()
    test_data_context["iframe结果"] = result


@then("iframe 操作应该成功")
def verify_iframe_success(test_data_context):
    assert test_data_context.get("iframe结果") is not None, "iframe 操作失败"

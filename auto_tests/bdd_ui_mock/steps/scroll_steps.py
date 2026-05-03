# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 页面滚动 BDD 步骤定义
# @Time   : 2026-05-03
# @Author : 毛鹏
from pytest_bdd import when, then

from auto_tests.bdd_ui_mock.page_object.home import HomePage
from auto_tests.bdd_ui_mock.page_object.scroll import ScrollPage


@when("用户进入页面滚动页面")
def user_enter_scroll(logged_in_user, page_context):
    home = page_context.get("首页")
    if not home:
        home = HomePage(logged_in_user["base_data"], logged_in_user["base_data"].test_data)
        home.goto()
        page_context["首页"] = home
    home.test_data.set_cache('菜单名称', '滚动操作测试')
    home.switch_menu()
    scroll = ScrollPage(logged_in_user["base_data"], logged_in_user["base_data"].test_data)
    page_context["滚动"] = scroll


@when("用户执行页面滚动操作")
def user_perform_scroll(logged_in_user, page_context, test_data_context):
    scroll = page_context["滚动"]
    result = scroll.test_scroll()
    test_data_context["滚动结果"] = result


@then("页面滚动应该成功")
def verify_scroll_success(test_data_context):
    assert test_data_context.get("滚动结果") is not None, "页面滚动失败"

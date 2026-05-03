# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 页面导航 BDD 步骤定义
# @Time   : 2026-05-03
# @Author : 毛鹏
from pytest_bdd import when, then

from auto_tests.bdd_ui_mock.page_object.home import HomePage
from auto_tests.bdd_ui_mock.page_object.navigation import NavigationPage


@when("用户进入页面导航页面")
def user_enter_navigation(logged_in_user, page_context):
    home = page_context.get("首页")
    if not home:
        home = HomePage(logged_in_user["base_data"], logged_in_user["base_data"].test_data)
        home.goto()
        page_context["首页"] = home
    home.test_data.set_cache('菜单名称', '页面导航测试')
    home.switch_menu()
    nav_page = NavigationPage(logged_in_user["base_data"], logged_in_user["base_data"].test_data)
    page_context["导航"] = nav_page


@when("用户执行页面导航操作")
def user_perform_navigation(logged_in_user, page_context, test_data_context):
    nav_page = page_context["导航"]
    result = nav_page.test_navigation()
    test_data_context["导航结果"] = result


@then("页面导航应该成功")
def verify_navigation_success(test_data_context):
    assert test_data_context.get("导航结果") is not None, "页面导航失败"

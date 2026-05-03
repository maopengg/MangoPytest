# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 闪现元素 BDD 步骤定义
# @Time   : 2026-05-03
# @Author : 毛鹏
from pytest_bdd import when, then

from auto_tests.bdd_ui_mock.page_object.home_page import HomePage
from auto_tests.bdd_ui_mock.page_object.flash_page import FlashPage


@when("用户进入闪现元素页面")
def user_enter_flash_page(logged_in_user, page_context):
    home = page_context.get("首页")
    if not home:
        home = HomePage(logged_in_user["base_data"], logged_in_user["base_data"].test_data)
        home.goto()
        page_context["首页"] = home
    home.test_data.set_cache('菜单名称', '闪现元素测试')
    home.switch_menu()
    flash_page = FlashPage(logged_in_user["base_data"], logged_in_user["base_data"].test_data)
    page_context["闪现"] = flash_page


@when("用户捕获闪现元素")
def user_capture_flash_element(logged_in_user, page_context, test_data_context):
    flash_page = page_context["闪现"]
    result = flash_page.test_flash_element()
    test_data_context["闪现结果"] = result


@then("闪现元素捕获应该成功")
def verify_flash_success(test_data_context):
    assert test_data_context.get("闪现结果") is not None, "闪现元素捕获失败"

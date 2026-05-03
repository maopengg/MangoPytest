# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 批量操作 BDD 步骤定义
# @Time   : 2026-05-03
# @Author : 毛鹏
from pytest_bdd import when, then

from auto_tests.bdd_ui_mock.page_object.home import HomePage
from auto_tests.bdd_ui_mock.page_object.batch import BatchPage


@when("用户进入批量操作页面")
def user_enter_batch(logged_in_user, page_context):
    home = page_context.get("首页")
    if not home:
        home = HomePage(logged_in_user["base_data"], logged_in_user["base_data"].test_data)
        home.goto()
        page_context["首页"] = home
    home.test_data.set_cache('菜单名称', '批量操作测试')
    home.switch_menu()
    batch = BatchPage(logged_in_user["base_data"], logged_in_user["base_data"].test_data)
    page_context["批量"] = batch


@when("用户执行批量勾选操作")
def user_perform_batch_checkbox(logged_in_user, page_context, test_data_context):
    batch = page_context["批量"]
    result = batch.test_batch_checkbox()
    test_data_context["批量结果"] = result


@then("批量操作应该成功")
def verify_batch_success(test_data_context):
    assert test_data_context.get("批量结果") is not None, "批量操作失败"

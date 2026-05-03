# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 首页 BDD 步骤定义
# @Time   : 2026-05-03
# @Author : 毛鹏
from pytest_bdd import given, then

from auto_tests.bdd_ui_mock.page_object.home import HomePage


@given("用户访问 Mock 首页")
def user_visit_mock_home(logged_in_user, page_context):
    home = HomePage(logged_in_user["base_data"], logged_in_user["base_data"].test_data)
    home.goto()
    page_context["首页"] = home


@then("页面加载成功")
def verify_page_loaded(page_context):
    assert page_context.get("首页") is not None, "首页未加载"

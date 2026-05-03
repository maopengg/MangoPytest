# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 文件上传 BDD 步骤定义
# @Time   : 2026-05-03
# @Author : 毛鹏
import os

from pytest_bdd import when, then

from auto_tests.bdd_ui_mock.page_object.home_page import HomePage
from auto_tests.bdd_ui_mock.page_object.upload_page import UploadPage


@when("用户进入文件上传页面")
def user_enter_upload_page(logged_in_user, page_context):
    home = page_context.get("首页")
    if not home:
        home = HomePage(logged_in_user["base_data"], logged_in_user["base_data"].test_data)
        home.goto()
        page_context["首页"] = home
    home.test_data.set_cache('菜单名称', '文件上传测试')
    home.switch_menu()
    upload_page = UploadPage(logged_in_user["base_data"], logged_in_user["base_data"].test_data)
    page_context["上传"] = upload_page


@when("用户上传测试文件")
def user_upload_test_file(logged_in_user, page_context, test_data_context):
    upload_page = page_context["上传"]
    file_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "upload", "测试上传文件UI.xlsx"
    )
    result = upload_page.test_upload_file(file_path)
    test_data_context["上传结果"] = result


@then("文件上传应该成功")
def verify_upload_success(test_data_context):
    assert test_data_context.get("上传结果") is not None, "文件上传失败"

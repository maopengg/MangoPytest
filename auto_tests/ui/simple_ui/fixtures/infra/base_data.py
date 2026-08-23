# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: UI 基础数据 Fixtures
# @Time   : 2026-04-25
# @Author : 毛鹏
"""
UI 基础数据 Fixtures 模块

提供 UI 测试基础数据相关的 fixtures：
- base_data: UI 测试基础数据对象（function 级别）
"""

import pytest
from mangoautomation.uidrives import BaseData as BaseDataDrives

from core.utils import log, project_dir
from core.utils.obtain_test_data import ObtainTestData


@pytest.fixture(scope="function")
def base_data(web_runtime, request):
    """
    UI 测试基础数据对象 fixture

    每个测试函数创建新的页面上下文，测试结束后自动清理

    使用示例：
        def test_example(base_data):
            from auto_tests.ui.simple_ui.abstract.home_page import HomePage
            home_page = HomePage(base_data, test_data)
            home_page.goto()
    """
    # w_tap 需要具备触摸能力的浏览器上下文。仅为对应参数化用例启用
    # Playwright 设备模拟，其他桌面 UI 用例仍使用默认桌面上下文。
    callspec = getattr(request.node, "callspec", None)
    params = callspec.params if callspec else {}
    operation_case = params.get("operation_case")
    element_case = params.get("element_case")
    needs_touch = (
        getattr(operation_case, "method", None) == "w_tap"
        or getattr(element_case, "element_id", None) == "tap-target"
    )
    browser_runtime = web_runtime.browser_runtime
    previous_device = browser_runtime.web_h5
    if needs_touch:
        browser_runtime.web_h5 = "iPhone 13"
    try:
        context, page = web_runtime.new_context_page()
    finally:
        browser_runtime.web_h5 = previous_device

    # 获取 test_data（如果测试类中有定义）
    test_data = ObtainTestData()
    if hasattr(request.instance, 'test_data') and request.instance.test_data:
        test_data = request.instance.test_data

    # 创建 BaseData 对象
    base_data_obj = BaseDataDrives(test_data, log)
    base_data_obj.bind_web(web_runtime, context, page)
    base_data_obj.set_file_path(project_dir.download(), project_dir.screenshot())

    yield base_data_obj

    # 测试结束后清理
    try:
        context.close()
        page.close()
    except Exception as e:
        log.debug(f"清理页面上下文时出错: {e}")

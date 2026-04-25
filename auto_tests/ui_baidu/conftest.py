# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: UI Baidu 项目 Fixtures
# @Time   : 2026-04-25
# @Author : 毛鹏
"""
UI Baidu 项目的 Pytest Fixtures

提供：
- driver_object: Web 驱动对象
- base_data: UI 测试基础数据对象
"""

import pytest
from mangoautomation.uidrive import DriverObject, BaseData
from mangoautomation.uidrives import BaseData as BaseDataDrives

from core.enums.ui_enum import BrowserTypeEnum
from core.utils import log, project_dir
from core.utils.obtain_test_data import ObtainTestData


@pytest.fixture(scope="session")
def driver_object():
    """
    Web 驱动对象 fixture
    
    整个测试会话期间共享一个驱动对象
    """
    driver = DriverObject(log)
    driver.set_web(web_type=BrowserTypeEnum.CHROMIUM.value, web_max=True)
    yield driver
    # 会话结束时清理
    try:
        driver.web.close()
    except Exception:
        pass


@pytest.fixture(scope="function")
def base_data(driver_object, request):
    """
    UI 测试基础数据对象 fixture
    
    每个测试函数创建新的页面上下文，测试结束后自动清理
    
    使用示例：
        def test_example(base_data):
            page = HomePage(base_data, test_data)
            page.goto()
    """
    # 创建新的页面上下文
    context, page = driver_object.web.new_web_page()
    
    # 获取 test_data（如果测试类中有定义）
    test_data = ObtainTestData()
    if hasattr(request.instance, 'test_data') and request.instance.test_data:
        test_data = request.instance.test_data
    
    # 创建 BaseData 对象
    base_data_obj = BaseDataDrives(test_data, log)
    base_data_obj.set_page_context(page, context)
    base_data_obj.set_file_path(project_dir.download(), project_dir.screenshot())
    
    yield base_data_obj
    
    # 测试结束后清理
    try:
        context.close()
        page.close()
    except Exception as e:
        log.debug(f"清理页面上下文时出错: {e}")

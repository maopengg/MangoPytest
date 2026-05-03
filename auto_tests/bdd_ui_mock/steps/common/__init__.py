# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: BDD UI Mock 公共 Fixtures
# @Time   : 2026-05-03
# @Author : 毛鹏
"""BDD UI Mock 公共 Fixtures — 参照 qfei_contract_ui/steps/common/__init__.py"""
import pytest
from mangoautomation.uidrive import DriverObject
from mangoautomation.uidrives import BaseData as BaseDataDrives

from core.enums.ui_enum import BrowserTypeEnum
from core.utils import log, project_dir
from core.utils.obtain_test_data import ObtainTestData


@pytest.fixture(scope="session")
def driver_object():
    driver = DriverObject(log)
    driver.set_web(web_type=BrowserTypeEnum.CHROMIUM.value, web_max=True)
    yield driver
    try:
        driver.web.close()
    except Exception:
        pass


@pytest.fixture(scope="function")
def base_data(driver_object):
    context, page = driver_object.web.new_web_page()
    test_data = ObtainTestData()
    base_data_obj = BaseDataDrives(test_data, log)
    base_data_obj.set_page_context(page, context)
    base_data_obj.set_file_path(project_dir.download(), project_dir.screenshot())
    yield base_data_obj
    try:
        context.close()
        page.close()
    except Exception as e:
        log.debug(f"清理页面上下文时出错: {e}")


@pytest.fixture
def page_context():
    """步骤间传递 Page Object 实例"""
    return {}


@pytest.fixture
def test_data_context():
    """步骤间传递业务数据"""
    return {}


@pytest.fixture
def logged_in_user(base_data):
    """BDD 步骤统一入口"""
    return {"base_data": base_data}

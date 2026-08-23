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

import hashlib
import json
import os
from pathlib import Path

import allure
import pytest
from mangoautomation.uidrives import BaseData as BaseDataDrives
from playwright.sync_api import Error as PlaywrightError

from auto_tests.ui.pytest_ui.config import settings
from core.utils import log, project_dir
from core.utils.obtain_test_data import ObtainTestData


@pytest.fixture(scope="function")
def base_data(web_runtime, request):
    """
    UI 测试基础数据对象 fixture

    每个测试函数创建新的页面上下文，测试结束后自动清理

    使用示例：
        def test_example(base_data):
            from auto_tests.ui.pytest_ui.page_object.home_page import HomePage
            home_page = HomePage(base_data, test_data)
            home_page.goto()
    """
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

    worker_id = os.getenv("PYTEST_XDIST_WORKER", "gw0")
    node_hash = hashlib.sha1(request.node.nodeid.encode("utf-8")).hexdigest()[:12]
    artifact_dir = (
        Path(project_dir.root_path()) / settings.ARTIFACT_DIR / worker_id / node_hash
    )
    artifact_dir.mkdir(parents=True, exist_ok=True)
    console_errors: list[str] = []
    page.on(
        "console",
        lambda message: console_errors.append(message.text)
        if message.type == "error"
        else None,
    )
    if settings.TRACE_ENABLED:
        context.tracing.start(screenshots=True, snapshots=True, sources=True)

    # 获取 test_data（如果测试类中有定义）
    test_data = ObtainTestData()
    if hasattr(request.instance, 'test_data') and request.instance.test_data:
        test_data = request.instance.test_data

    # 创建 BaseData 对象
    base_data_obj = BaseDataDrives(test_data, log)
    base_data_obj.bind_web(web_runtime, context, page)
    download_dir = artifact_dir / "downloads"
    screenshot_dir = artifact_dir / "screenshots"
    download_dir.mkdir(exist_ok=True)
    screenshot_dir.mkdir(exist_ok=True)
    base_data_obj.set_file_path(str(download_dir), str(screenshot_dir))
    base_data_obj.artifact_dir = artifact_dir
    base_data_obj.console_errors = console_errors

    yield base_data_obj

    report = getattr(request.node, "rep_call", None)
    failed = bool(report and report.failed)
    try:
        if failed and not page.is_closed():
            screenshot = artifact_dir / "failure.png"
            html = artifact_dir / "page.html"
            console = artifact_dir / "console-errors.json"
            page.screenshot(path=str(screenshot), full_page=True)
            html.write_text(page.content(), encoding="utf-8")
            console.write_text(
                json.dumps(console_errors, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            allure.attach.file(str(screenshot), name="失败页面截图")
            allure.attach.file(str(html), name="失败页面 HTML")
            allure.attach.file(str(console), name="浏览器控制台错误")
        if settings.TRACE_ENABLED:
            trace = artifact_dir / "trace.zip"
            context.tracing.stop(path=str(trace) if failed else None)
            if failed:
                allure.attach.file(str(trace), name="Playwright Trace")
    except (OSError, PlaywrightError) as error:
        log.warning(f"生成 UI 失败产物时出错: {error}")
    finally:
        try:
            context.close()
        except PlaywrightError as error:
            log.debug(f"清理页面上下文时出错: {error}")

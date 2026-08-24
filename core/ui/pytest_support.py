"""pytest 同步 UI 测试的公共浏览器生命周期。"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator, Protocol

from mangoautomation.uidrives import BaseData, WebDriverFactory
from playwright.sync_api import Error as PlaywrightError

from core.ui.artifacts import finish_ui_artifacts, start_ui_artifacts
from core.ui.runtime_cleanup import close_sync_web_runtime
from core.ui.runtime_options import sync_web_runtime_options
from core.utils.obtain_test_data import ObtainTestData


class UIExecutionSettings(Protocol):
    ARTIFACT_DIR: str
    TRACE_ENABLED: bool
    BROWSER: str
    BROWSER_PATH: str
    HEADLESS: bool
    IMPLICIT_WAIT: int


@contextmanager
def sync_web_runtime_session(settings: UIExecutionSettings, log) -> Iterator:
    """创建并可靠关闭一个 pytest Session 级同步 Web Runtime。"""
    runtime = WebDriverFactory.create_sync_runtime(
        **sync_web_runtime_options(settings, log)
    )
    try:
        yield runtime
    finally:
        close_sync_web_runtime(runtime, log)


@contextmanager
def temporary_web_device(web_runtime, device: str | None) -> Iterator[None]:
    """只在创建 Context 时临时切换 Playwright 设备。"""
    browser_runtime = web_runtime.browser_runtime
    previous_device = browser_runtime.web_h5
    if device:
        browser_runtime.web_h5 = device
    try:
        yield
    finally:
        browser_runtime.web_h5 = previous_device


def request_needs_touch(request, *, case_ids: set[str] | None = None) -> bool:
    """识别参数化或 BDD Case 是否需要触摸设备。"""
    callspec = getattr(request.node, "callspec", None)
    params = callspec.params if callspec else {}
    operation_case = params.get("operation_case")
    element_case = params.get("element_case")
    if (
        getattr(operation_case, "method", None) == "w_tap"
        or getattr(element_case, "element_id", None) == "tap-target"
    ):
        return True
    examples = params.get("_pytest_bdd_example", {})
    case_id = params.get("case_id") or examples.get("case_id", "")
    configured_ids = case_ids or set()
    return case_id in configured_ids or any(
        item in request.node.name for item in configured_ids
    )


@contextmanager
def ui_base_data_session(
    *,
    web_runtime,
    request,
    settings: UIExecutionSettings,
    log,
    device: str | None = None,
) -> Iterator[BaseData]:
    """创建 Case 级 Context、BaseData 和完整失败产物生命周期。"""
    with temporary_web_device(web_runtime, device):
        context, page = web_runtime.new_context_page()
    artifacts = None
    try:
        artifacts = start_ui_artifacts(
            page=page,
            context=context,
            settings=settings,
            node_id=request.node.nodeid,
        )
        test_data = ObtainTestData()
        instance_data = getattr(request.instance, "test_data", None)
        if instance_data:
            test_data = instance_data

        base_data = BaseData(test_data, log)
        base_data.bind_web(web_runtime, context, page)
        base_data.set_file_path(
            str(artifacts.download_directory),
            str(artifacts.screenshot_directory),
        )
        base_data.artifact_dir = artifacts.directory
        base_data.console_errors = artifacts.console_errors
        yield base_data
    finally:
        if artifacts is not None:
            report = getattr(request.node, "rep_call", None)
            finish_ui_artifacts(
                page=page,
                context=context,
                session=artifacts,
                failed=bool(report and report.failed),
                log=log,
            )
        try:
            context.close()
        except PlaywrightError as error:
            log.debug(f"清理页面上下文时出错: {error}")

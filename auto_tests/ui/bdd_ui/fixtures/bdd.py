"""bdd_ui 浏览器、上下文和数据工厂 Fixtures。"""

import hashlib
import json
import os
from pathlib import Path

import allure
import pytest
from mangoautomation.uidrives import BaseData as BaseDataDrives
from mangoautomation.uidrives import WebDriverFactory
from playwright.sync_api import Error as PlaywrightError

from auto_tests.ui.bdd_ui.config import settings
from auto_tests.ui.bdd_ui.contexts import (
    ClaimScenarioContext,
    OrderScenarioContext,
    ReviewScenarioContext,
)
from auto_tests.ui.bdd_ui.data_factory import BddUIDataFactory
from auto_tests.ui.bdd_ui.flows import ClaimFlow, OrderFlow, ReviewFlow
from auto_tests.ui.bdd_ui.page_object.business import ClaimPage, OrderPage, ReviewPage
from auto_tests.ui.bdd_ui.repositories import BddUIRepositories
from core.enums.ui_enum import BrowserTypeEnum
from core.ui.runtime_cleanup import close_sync_web_runtime
from core.utils import log, project_dir
from core.utils.obtain_test_data import ObtainTestData


@pytest.fixture(scope="session")
def web_runtime():
    runtime = WebDriverFactory.create_sync_runtime(
        web_type=BrowserTypeEnum.CHROMIUM.value,
        web_max=not settings.HEADLESS,
        web_headers=settings.HEADLESS,
        set_default_timeout=settings.IMPLICIT_WAIT,
        log=log,
    )
    yield runtime
    close_sync_web_runtime(runtime, log)


@pytest.fixture
def base_data(web_runtime, request):
    callspec = getattr(request.node, "callspec", None)
    params = callspec.params if callspec else {}
    example = params.get("_pytest_bdd_example", {})
    case_id = params.get("case_id") or example.get("case_id", "")
    node_name = request.node.name
    browser_runtime = web_runtime.browser_runtime
    previous_device = browser_runtime.web_h5
    if case_id in {"UI-OP-031", "UI-EL-044"} or any(
        value in node_name for value in ("UI-OP-031", "UI-EL-044")
    ):
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

    data = BaseDataDrives(ObtainTestData(), log)
    data.bind_web(web_runtime, context, page)
    download_dir = artifact_dir / "downloads"
    screenshot_dir = artifact_dir / "screenshots"
    download_dir.mkdir(exist_ok=True)
    screenshot_dir.mkdir(exist_ok=True)
    data.set_file_path(str(download_dir), str(screenshot_dir))
    data.artifact_dir = artifact_dir
    data.console_errors = console_errors
    yield data

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


@pytest.fixture
def bdd_ui_repositories():
    repositories = BddUIRepositories(
        settings.BASE_URL,
        timeout=settings.PAGE_LOAD_TIMEOUT,
    )
    yield repositories
    repositories.close()


@pytest.fixture
def bdd_ui_data_factory(bdd_ui_repositories):
    return BddUIDataFactory(bdd_ui_repositories)


@pytest.fixture
def order_flow(base_data):
    return OrderFlow(OrderPage(base_data))


@pytest.fixture
def claim_flow(base_data):
    return ClaimFlow(ClaimPage(base_data))


@pytest.fixture
def review_flow(base_data):
    return ReviewFlow(ReviewPage(base_data))


@pytest.fixture
def scenario_context() -> dict:
    return {}


@pytest.fixture
def order_context() -> OrderScenarioContext:
    return OrderScenarioContext()


@pytest.fixture
def claim_context() -> ClaimScenarioContext:
    return ClaimScenarioContext()


@pytest.fixture
def review_context() -> ReviewScenarioContext:
    return ReviewScenarioContext()

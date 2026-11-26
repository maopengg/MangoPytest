"""使用进程内 FastAPI 客户端验证浏览器页面，不启动 HTTP 服务。"""

from pathlib import Path

from fastapi.testclient import TestClient
import pytest
from playwright.sync_api import expect, sync_playwright

from web_console.app import create_app
from tests.web_console.factories import seed_run

pytestmark = pytest.mark.browser_e2e
BASE_URL = "http://console.example.test"


@pytest.fixture
def console_browser(console_settings, repository_root, monkeypatch):
    monkeypatch.setenv("PYTHONPATH", str(repository_root))
    monkeypatch.setenv("MANGO_PYTEST_RUNTIME_DIR", str(console_settings.runtime_root))
    app = create_app(console_settings)
    seed_run(app.state.services, console_settings)
    with TestClient(app, base_url=BASE_URL) as client:
        result = client.post("/api/projects/sample_api/collect")
        assert result.status_code == 200, result.text
        with sync_playwright() as playwright:
            chrome = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
            browser = playwright.chromium.launch(
                headless=True, executable_path=str(chrome) if chrome.is_file() else None,
            )
            try:
                page = browser.new_page(viewport={"width": 1440, "height": 1000})
                page.on("pageerror", lambda error: print(f"Browser error: {error}"))

                def dispatch(route):
                    request = route.request
                    headers = {key: value for key, value in request.all_headers().items()
                               if key not in {"host", "content-length"}}
                    response = client.request(
                        request.method, request.url, headers=headers,
                        content=request.post_data_buffer,
                    )
                    route.fulfill(status=response.status_code, body=response.content, headers={
                        key: value for key, value in response.headers.items()
                        if key not in {"content-length", "content-encoding", "transfer-encoding"}
                    })

                page.route(f"{BASE_URL}/**", dispatch)
                yield page, client
            finally:
                browser.close()


def exercise_console(page, check_page=None):
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.goto(BASE_URL)
    expect(page.locator(".project-card")).to_have_count(4)
    expect(page.locator(".run-row")).to_have_count(1)
    if check_page:
        check_page(page, "dashboard")

    page.goto(f"{BASE_URL}/projects/sample_api")
    expect(page.locator(".source-editor")).to_be_visible()
    expect(page.locator(".source-editor")).to_contain_text("test_ok")
    page.get_by_role("button", name="运行整个项目").click()
    expect(page.locator("#run-dialog")).to_be_visible()
    expect(page.locator("#runtime-options")).to_contain_text("服务地址")
    page.locator("#run-dialog .icon-button").click()
    if check_page:
        check_page(page, "project")

    page.goto(f"{BASE_URL}/runs/run-example")
    expect(page.locator("#allure-case-list .allure-case-row")).to_have_count(1)
    expect(page.locator("#allure-case-detail")).to_contain_text("UI-001 验证提交操作")
    page.get_by_role("button", name="测试结果", exact=True).click()
    expect(page.locator("#tab-cases")).to_be_visible()
    page.locator("#allure-search").fill("does-not-exist")
    expect(page.locator("#allure-case-list")).to_contain_text("没有匹配的用例")
    page.locator("#allure-search").fill("验证提交")
    expect(page.locator("#allure-case-list .allure-case-row")).to_have_count(1)
    page.get_by_role("button", name="全部产物", exact=True).click()
    expect(page.locator("#artifacts")).to_contain_text("example.txt")
    page.get_by_role("button", name="测试结果", exact=True).click()
    if check_page:
        check_page(page, "run_detail")
    assert errors == [], errors


def test_console_page_modules_and_interactions(console_browser):
    page, _ = console_browser
    exercise_console(page)

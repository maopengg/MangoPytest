from types import SimpleNamespace

import pytest

from core.ui.artifacts import finish_ui_artifacts, start_ui_artifacts
from core.ui.pytest_support import request_needs_touch, temporary_web_device


class FakeTracing:
    def __init__(self):
        self.started = False
        self.stopped_path = None

    def start(self, **kwargs):
        self.started = kwargs

    def stop(self, path=None):
        self.stopped_path = path
        if path:
            from pathlib import Path
            Path(path).write_bytes(b"trace")


class FakeContext:
    def __init__(self):
        self.tracing = FakeTracing()


class FakePage:
    def __init__(self):
        self.listeners = {}

    def on(self, event, callback):
        self.listeners[event] = callback

    def is_closed(self):
        return False

    def screenshot(self, path, full_page):
        from pathlib import Path
        Path(path).write_bytes(b"png")

    def content(self):
        return "<html>failed</html>"


def _request(params, name="test_case"):
    return SimpleNamespace(
        node=SimpleNamespace(
            callspec=SimpleNamespace(params=params),
            name=name,
        )
    )


def test_request_needs_touch_supports_pytest_and_bdd_cases():
    operation = SimpleNamespace(method="w_tap")
    assert request_needs_touch(_request({"operation_case": operation})) is True
    assert request_needs_touch(
        _request({"_pytest_bdd_example": {"case_id": "UI-OP-031"}}),
        case_ids={"UI-OP-031"},
    ) is True
    assert request_needs_touch(_request({})) is False


def test_temporary_web_device_always_restores_previous_value():
    browser_runtime = SimpleNamespace(web_h5="desktop")
    runtime = SimpleNamespace(browser_runtime=browser_runtime)

    with pytest.raises(RuntimeError):
        with temporary_web_device(runtime, "iPhone 13"):
            assert browser_runtime.web_h5 == "iPhone 13"
            raise RuntimeError("stop")

    assert browser_runtime.web_h5 == "desktop"


def test_ui_artifacts_capture_failure_and_trace(tmp_path, monkeypatch):
    page = FakePage()
    context = FakeContext()
    settings = SimpleNamespace(ARTIFACT_DIR=str(tmp_path), TRACE_ENABLED=True)
    attached = []
    monkeypatch.setattr(
        "core.ui.artifacts.allure.attach.file",
        lambda path, name: attached.append((path, name)),
    )

    session = start_ui_artifacts(
        page=page,
        context=context,
        settings=settings,
        node_id="tests/test_demo.py::test_failure",
    )
    page.listeners["console"](SimpleNamespace(type="error", text="boom"))
    finish_ui_artifacts(
        page=page,
        context=context,
        session=session,
        failed=True,
        log=SimpleNamespace(warning=lambda message: None),
    )

    assert (session.directory / "failure.png").is_file()
    assert (session.directory / "page.html").is_file()
    assert (session.directory / "console-errors.json").read_text() == '[\n  "boom"\n]'
    assert (session.directory / "trace.zip").is_file()
    assert {name for _, name in attached} == {
        "失败页面截图",
        "失败页面 HTML",
        "浏览器控制台错误",
        "Playwright Trace",
    }

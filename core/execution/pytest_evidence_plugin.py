"""Pytest plugin that automatically captures complete Allure test evidence."""

from __future__ import annotations

from functools import wraps
import inspect
import time
from typing import Any

import allure
import pytest

from core.execution.evidence import attach_json, safe_value, ui_call_evidence
from core.execution.data_lineage import (
    current_lineage,
    instrument_lineage_object,
    start_lineage,
    stop_lineage,
)


_PATCHED = False

_ELEMENT_SNAPSHOT_SCRIPT = """
element => {
  const rect = element.getBoundingClientRect();
  const style = window.getComputedStyle(element);
  const attributes = {};
  for (const name of ['id', 'name', 'type', 'role', 'aria-label', 'aria-disabled',
                      'placeholder', 'title', 'data-testid', 'class']) {
    const value = element.getAttribute(name);
    if (value !== null && value !== '') attributes[name] = value;
  }
  const text = String(element.innerText || element.textContent || '').trim().slice(0, 2000);
  const hasValue = 'value' in element;
  const disabled = Boolean(element.disabled) || element.getAttribute('aria-disabled') === 'true';
  return {
    tag_name: element.tagName.toLowerCase(),
    text,
    value: hasValue ? element.value : null,
    attributes,
    visible: Boolean(rect.width && rect.height) && style.visibility !== 'hidden' && style.display !== 'none',
    enabled: !disabled,
    editable: Boolean(element.isContentEditable || ['input', 'textarea', 'select'].includes(element.tagName.toLowerCase())) && !disabled,
    bounding_box: {x: rect.x, y: rect.y, width: rect.width, height: rect.height},
  };
}
"""


def _looks_like_locator(value: Any) -> bool:
    return (
        callable(getattr(value, "count", None))
        and callable(getattr(getattr(value, "first", None), "evaluate", None))
    )


def _locator_snapshot(locator: Any, *, reference: str, source: str) -> dict[str, Any]:
    """Collect an ElementResultModel-like snapshot without changing test behavior."""
    snapshot: dict[str, Any] = {
        "reference": reference,
        "source": source,
        "locator": repr(locator),
        "match_count": 0,
        "element": None,
    }
    try:
        snapshot["match_count"] = locator.count()
        if snapshot["match_count"]:
            snapshot["element"] = locator.first.evaluate(_ELEMENT_SNAPSHOT_SCRIPT, timeout=500)
    except Exception as error:  # Element evidence must never break the actual UI operation.
        snapshot["snapshot_error"] = f"{type(error).__name__}: {error}"
    return safe_value(snapshot)


def _ui_operation_evidence(name: str, args: tuple[Any, ...], kwargs: dict[str, Any]) -> dict[str, Any]:
    payload = ui_call_evidence(name, args, kwargs)
    snapshots = []
    for index, value in enumerate(args):
        if not _looks_like_locator(value):
            continue
        reference = f"element-{len(snapshots) + 1}"
        snapshots.append(_locator_snapshot(value, reference=reference, source=f"位置参数 {index + 1}"))
        payload["arguments"][index] = {"element_reference": reference}
    for key, value in kwargs.items():
        if not _looks_like_locator(value):
            continue
        reference = f"element-{len(snapshots) + 1}"
        snapshots.append(_locator_snapshot(value, reference=reference, source=f"关键字参数 {key}"))
        payload["keyword_arguments"][key] = {"element_reference": reference}
    if snapshots:
        payload["elements"] = snapshots
    return payload


def _case_id(item: pytest.Item) -> str:
    for marker_name in ("case_id", "testcase", "case"):
        marker = item.get_closest_marker(marker_name)
        if marker and marker.args:
            return str(marker.args[0])
    return ""


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_call(item: pytest.Item):
    """Attach identity and resolved parametrized inputs to the test body itself."""
    node = item
    markers = [marker.name for marker in node.iter_markers()]
    attach_json("Case 信息", {
        "name": node.name,
        "case_id": _case_id(node),
        "node_id": node.nodeid,
        "file": str(getattr(node, "path", "")),
        "line": getattr(node, "location", (None, None, None))[1] + 1,
        "markers": list(dict.fromkeys(markers)),
        "description": inspect.getdoc(getattr(node, "obj", None)) or "",
    })
    callspec = getattr(node, "callspec", None)
    attach_json("测试数据", {
        "parameters": safe_value(callspec.params if callspec else {}),
        "fixtures": list(getattr(node, "fixturenames", [])),
    })
    try:
        yield
    finally:
        lineage = current_lineage()
        if lineage and lineage.nodes:
            attach_json("数据血缘", lineage.export())


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo):
    """把 setup/call/teardown 结果暴露给资源 Fixture。"""
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item: pytest.Item) -> None:
    start_lineage(item.nodeid)


@pytest.hookimpl(hookwrapper=True)
def pytest_fixture_setup(fixturedef, request):
    outcome = yield
    if outcome.excinfo is None:
        instrument_lineage_object(outcome.get_result())


@pytest.hookimpl(trylast=True)
def pytest_runtest_teardown(item: pytest.Item) -> None:
    stop_lineage()


def _patch_method(owner: type, method_name: str) -> None:
    original = owner.__dict__.get(method_name)
    if not callable(original) or getattr(original, "__mango_evidence__", False):
        return

    @wraps(original)
    def wrapped(self, *args, **kwargs):
        started = time.perf_counter()
        with allure.step(f"UI 操作 · {method_name}"):
            attach_json("操作信息", _ui_operation_evidence(method_name, args, kwargs))
            try:
                result = original(self, *args, **kwargs)
            except Exception as error:
                attach_json("操作结果", {
                    "status": "failed",
                    "duration_ms": round((time.perf_counter() - started) * 1000, 2),
                    "error_type": type(error).__name__,
                    "error": str(error),
                    "page_url": getattr(getattr(getattr(self, "base_data", None), "page", None), "url", ""),
                })
                page = getattr(getattr(self, "base_data", None), "page", None)
                if page is not None:
                    try:
                        allure.attach(page.screenshot(full_page=True), "失败页面截图", allure.attachment_type.PNG)
                    except Exception:
                        pass
                raise
            attach_json("操作结果", {
                "status": "passed",
                "duration_ms": round((time.perf_counter() - started) * 1000, 2),
                "return_value": safe_value(result),
                "page_url": getattr(getattr(getattr(self, "base_data", None), "page", None), "url", ""),
            })
            return result

    wrapped.__mango_evidence__ = True
    setattr(owner, method_name, wrapped)


def pytest_configure(config: pytest.Config) -> None:
    """Patch mangoautomation once so all three UI project styles share reporting."""
    global _PATCHED
    if _PATCHED:
        return
    try:
        from mangoautomation.uidrives import SyncWebDevice
        from mangoautomation.uidrives.web import SyncWebAssertion
    except ImportError:
        return
    for root in (SyncWebDevice, SyncWebAssertion):
        for owner in root.mro():
            for name in tuple(owner.__dict__):
                if name.startswith(("w_", "a_")):
                    _patch_method(owner, name)
    _PATCHED = True

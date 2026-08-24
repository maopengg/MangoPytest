"""UI 测试产物目录、浏览器日志、截图与 Trace 公共能力。"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path

import allure
from playwright.sync_api import Error as PlaywrightError

from core.utils import project_dir


@dataclass(frozen=True)
class UIArtifactSession:
    directory: Path
    download_directory: Path
    screenshot_directory: Path
    console_errors: list[str]
    trace_enabled: bool


def start_ui_artifacts(*, page, context, settings, node_id: str) -> UIArtifactSession:
    """初始化单条 UI Case 的隔离产物目录并开始采集。"""
    worker_id = os.getenv("PYTEST_XDIST_WORKER", "gw0")
    node_hash = hashlib.sha1(node_id.encode("utf-8")).hexdigest()[:12]
    directory = Path(project_dir.root_path()) / str(settings.ARTIFACT_DIR) / worker_id / node_hash
    download_directory = directory / "downloads"
    screenshot_directory = directory / "screenshots"
    download_directory.mkdir(parents=True, exist_ok=True)
    screenshot_directory.mkdir(parents=True, exist_ok=True)

    console_errors: list[str] = []
    page.on(
        "console",
        lambda message: console_errors.append(message.text)
        if message.type == "error"
        else None,
    )
    trace_enabled = bool(getattr(settings, "TRACE_ENABLED", False))
    if trace_enabled:
        context.tracing.start(screenshots=True, snapshots=True, sources=True)
    return UIArtifactSession(
        directory=directory,
        download_directory=download_directory,
        screenshot_directory=screenshot_directory,
        console_errors=console_errors,
        trace_enabled=trace_enabled,
    )


def finish_ui_artifacts(*, page, context, session: UIArtifactSession, failed: bool, log) -> None:
    """结束采集，并在失败时保存结构化浏览器现场。"""
    if failed and not page.is_closed():
        try:
            screenshot = session.directory / "failure.png"
            html = session.directory / "page.html"
            console = session.directory / "console-errors.json"
            page.screenshot(path=str(screenshot), full_page=True)
            html.write_text(page.content(), encoding="utf-8")
            console.write_text(
                json.dumps(session.console_errors, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            allure.attach.file(str(screenshot), name="失败页面截图")
            allure.attach.file(str(html), name="失败页面 HTML")
            allure.attach.file(str(console), name="浏览器控制台错误")
        except (OSError, PlaywrightError) as error:
            log.warning(f"生成 UI 失败现场时出错: {error}")

    if not session.trace_enabled:
        return
    try:
        trace = session.directory / "trace.zip"
        context.tracing.stop(path=str(trace) if failed else None)
        if failed:
            allure.attach.file(str(trace), name="Playwright Trace")
    except (OSError, PlaywrightError) as error:
        log.warning(f"生成 Playwright Trace 时出错: {error}")

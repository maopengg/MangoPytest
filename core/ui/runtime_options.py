"""Translate project UI settings into mangoautomation runtime arguments."""

from __future__ import annotations

from core.enums.ui_enum import BrowserTypeEnum


_BROWSER_TYPES = {
    "chromium": BrowserTypeEnum.CHROMIUM.value,
    "chrome": BrowserTypeEnum.CHROMIUM.value,
    "edge": BrowserTypeEnum.EDGE.value,
    "firefox": BrowserTypeEnum.FIREFOX.value,
    "webkit": BrowserTypeEnum.WEBKIT.value,
}


def sync_web_runtime_options(settings, log) -> dict:
    browser = str(settings.BROWSER).lower()
    if browser not in _BROWSER_TYPES:
        raise ValueError(f"不支持的浏览器类型: {settings.BROWSER}")
    return {
        "web_type": _BROWSER_TYPES[browser],
        "web_path": settings.BROWSER_PATH or None,
        "web_max": not settings.HEADLESS,
        "web_headers": settings.HEADLESS,
        "set_default_timeout": settings.IMPLICIT_WAIT,
        "log": log,
    }

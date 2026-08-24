"""Allure execution evidence helpers shared by API and UI automation."""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import asdict, is_dataclass
import json
from pathlib import Path
from typing import Any, Iterator

import allure
from allure_commons.types import AttachmentType


_MAX_TEXT = 200_000


def safe_value(value: Any, *, key: str = "", depth: int = 0) -> Any:
    """Convert arbitrary test values to bounded, JSON-safe data."""
    if depth > 8:
        return "<max-depth>"
    if value is None or isinstance(value, (bool, int, float)):
        return value
    if isinstance(value, str):
        return value if len(value) <= _MAX_TEXT else value[:_MAX_TEXT] + "…<truncated>"
    if isinstance(value, bytes):
        return {"type": "bytes", "size": len(value), "preview": value[:100].hex()}
    if isinstance(value, Path):
        return str(value)
    if hasattr(value, "model_dump"):
        return safe_value(value.model_dump(), key=key, depth=depth + 1)
    if is_dataclass(value):
        return safe_value(asdict(value), key=key, depth=depth + 1)
    if isinstance(value, dict):
        return {
            str(item_key): safe_value(item_value, key=str(item_key), depth=depth + 1)
            for item_key, item_value in value.items()
        }
    if isinstance(value, (list, tuple, set)):
        return [safe_value(item, depth=depth + 1) for item in list(value)[:1000]]
    # Playwright Locator repr is useful and bounded; protobuf supports ListFields.
    if hasattr(value, "ListFields"):
        return {
            field.name: safe_value(item, key=field.name, depth=depth + 1)
            for field, item in value.ListFields()
        }
    text = repr(value)
    return text if len(text) <= 4000 else text[:4000] + "…<truncated>"


def attach_json(name: str, value: Any) -> None:
    allure.attach(
        json.dumps(safe_value(value), ensure_ascii=False, indent=2, default=str),
        name=name,
        attachment_type=AttachmentType.JSON,
    )


@contextmanager
def evidence_step(name: str, *, request: Any | None = None) -> Iterator[None]:
    with allure.step(name):
        if request is not None:
            attach_json("请求信息", request)
        yield


def response_evidence(
    *, status: Any = None, headers: Any = None, body: Any = None, elapsed_ms: float | None = None
) -> None:
    attach_json("响应信息", {
        "status": status,
        "elapsed_ms": round(elapsed_ms, 2) if elapsed_ms is not None else None,
        "headers": headers,
        "body": body,
    })


def ui_call_evidence(name: str, args: tuple[Any, ...], kwargs: dict[str, Any]) -> dict[str, Any]:
    return {
        "operation": name,
        "arguments": safe_value(list(args)),
        "keyword_arguments": safe_value(kwargs),
    }

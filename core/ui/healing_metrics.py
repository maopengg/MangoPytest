"""元素自愈与 AI 定位的运行级统计。

现状：单次操作的自愈结果已经落在 ``ElementResultModel.locator_engine`` 里，并作为
Allure 附件可见；但一轮运行"到底用了多少次 AI、救回了什么、熔断了没有"没有汇总。
本模块提供进程内累加器，由证据插件在会话结束时落盘，供控制台读取。

xdist 下每个 worker 是独立进程，因此文件名带上 worker 标识，读取方按通配符合并。
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import json
import os
from pathlib import Path
from threading import Lock
from typing import Any

#: 视为"未经过自愈"的定位来源。
FIXED_LOCATOR_SOURCE = "fixed_locator"

#: 落盘文件名前缀；读取方应按 ``ai-healing-summary*.json`` 合并。
SUMMARY_FILE_PREFIX = "ai-healing-summary"


@dataclass(frozen=True, slots=True)
class HealingEvent:
    """一次元素操作产生的自愈观测记录。"""

    element_name: str
    case_id: str = ""
    used_source: str = FIXED_LOCATOR_SOURCE
    used_ai: bool = False
    temporary_heal_used: bool = False
    final_score: float | None = None
    model: str | None = None
    prompt_version: str | None = None
    operation_failed: bool = False

    @property
    def healed(self) -> bool:
        """是否走了固定定位以外的路径（即发生了自愈）。"""

        return self.used_source not in ("", FIXED_LOCATOR_SOURCE) or self.temporary_heal_used

    @property
    def healed_successfully(self) -> bool:
        return self.healed and not self.operation_failed


@dataclass
class HealingMetricsRecorder:
    """进程内累加器。"""

    _events: list[HealingEvent] = field(default_factory=list)
    _lock: Lock = field(default_factory=Lock, repr=False)

    def record(self, event: HealingEvent) -> None:
        with self._lock:
            self._events.append(event)

    def reset(self) -> None:
        with self._lock:
            self._events.clear()

    def events(self) -> tuple[HealingEvent, ...]:
        with self._lock:
            return tuple(self._events)

    def snapshot(self) -> dict[str, Any]:
        """返回可直接展示/落盘的汇总结构。"""

        events = self.events()
        healed = [item for item in events if item.healed]
        ai_events = [item for item in events if item.used_ai]
        by_element: dict[str, int] = {}
        by_source: dict[str, int] = {}
        for item in healed:
            by_element[item.element_name] = by_element.get(item.element_name, 0) + 1
        for item in events:
            by_source[item.used_source] = by_source.get(item.used_source, 0) + 1
        models = sorted({item.model for item in events if item.model})
        prompt_versions = sorted(
            {item.prompt_version for item in events if item.prompt_version}
        )
        return {
            "operations": len(events),
            "healed_operations": len(healed),
            "healed_successfully": sum(1 for item in healed if item.healed_successfully),
            "healed_failed": sum(1 for item in healed if item.operation_failed),
            "ai_operations": len(ai_events),
            "ai_healed_successfully": sum(
                1 for item in ai_events if item.healed_successfully
            ),
            "local_healed": sum(1 for item in healed if not item.used_ai),
            "by_source": dict(sorted(by_source.items(), key=lambda kv: (-kv[1], kv[0]))),
            "by_element": dict(
                sorted(by_element.items(), key=lambda kv: (-kv[1], kv[0]))[:20]
            ),
            "models": models,
            "prompt_versions": prompt_versions,
            "events": [asdict(item) for item in events],
        }


#: 全局累加器：证据插件与元素运行时共享。
healing_metrics = HealingMetricsRecorder()


def summary_filename() -> str:
    """按 worker 区分文件名，避免 xdist 下互相覆盖。"""

    worker = os.getenv("PYTEST_XDIST_WORKER", "").strip()
    return f"{SUMMARY_FILE_PREFIX}-{worker}.json" if worker else f"{SUMMARY_FILE_PREFIX}.json"


def write_summary(directory: Path | str) -> Path | None:
    """把当前汇总写入目录；没有产生任何记录时不落盘。"""

    payload = healing_metrics.snapshot()
    if not payload["operations"]:
        return None
    target_dir = Path(directory)
    target_dir.mkdir(parents=True, exist_ok=True)
    path = target_dir / summary_filename()
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def merge_summaries(directory: Path | str) -> dict[str, Any] | None:
    """合并目录下所有 worker 的汇总文件。"""

    files = sorted(Path(directory).glob(f"{SUMMARY_FILE_PREFIX}*.json"))
    if not files:
        return None
    merged: dict[str, Any] = {
        "operations": 0, "healed_operations": 0, "healed_successfully": 0,
        "healed_failed": 0, "ai_operations": 0, "ai_healed_successfully": 0,
        "local_healed": 0, "by_source": {}, "by_element": {},
        "models": [], "prompt_versions": [], "workers": [],
    }
    for path in files:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(payload, dict):
            continue
        for key in (
            "operations", "healed_operations", "healed_successfully",
            "healed_failed", "ai_operations", "ai_healed_successfully", "local_healed",
        ):
            merged[key] += int(payload.get(key) or 0)
        for key in ("by_source", "by_element"):
            for name, count in (payload.get(key) or {}).items():
                merged[key][name] = merged[key].get(name, 0) + int(count or 0)
        merged["models"] = sorted(set(merged["models"]) | set(payload.get("models") or []))
        merged["prompt_versions"] = sorted(
            set(merged["prompt_versions"]) | set(payload.get("prompt_versions") or [])
        )
        merged["workers"].append(path.name)
    merged["by_element"] = dict(
        sorted(merged["by_element"].items(), key=lambda kv: (-kv[1], kv[0]))[:20]
    )
    merged["by_source"] = dict(
        sorted(merged["by_source"].items(), key=lambda kv: (-kv[1], kv[0]))
    )
    return merged


__all__ = [
    "FIXED_LOCATOR_SOURCE",
    "SUMMARY_FILE_PREFIX",
    "HealingEvent",
    "HealingMetricsRecorder",
    "healing_metrics",
    "merge_summaries",
    "summary_filename",
    "write_summary",
]

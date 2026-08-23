"""读取 Allure 原始结果，生成前端可直接消费的结构化数据。"""

from __future__ import annotations

from collections import Counter, defaultdict
import json
from pathlib import Path
import re
from typing import Any


_SECRET_PATTERN = re.compile(r"(?i)(authorization|token|password|secret|cookie)(\s*[:=]\s*)([^\s,;]+)")
_TEXT_TYPES = {"text/plain", "application/json", "text/csv", "text/html", "application/xml", "text/xml"}


def _scrub(value: str) -> str:
    return _SECRET_PATTERN.sub(r"\1\2***", value)


class AllureResultService:
    def __init__(self, artifact_dir: Path) -> None:
        self.artifact_dir = artifact_dir.resolve()
        self.results_dir = self.artifact_dir / "allure-results"

    def report(self) -> dict[str, Any]:
        results = self._load_documents("*-result.json")
        containers = self._load_documents("*-container.json")
        fixtures: dict[str, dict[str, list]] = defaultdict(lambda: {"befores": [], "afters": []})
        for container in containers:
            for child in container.get("children", []):
                fixtures[child]["befores"].extend(self._normalize_steps(container.get("befores", [])))
                fixtures[child]["afters"].extend(self._normalize_steps(container.get("afters", [])))

        tests = [self._normalize_result(result, fixtures.get(result.get("uuid", ""), {})) for result in results]
        tests.sort(key=lambda item: (item["start"] or 0, item["name"]))
        status_counts = Counter(test["status"] for test in tests)
        starts = [test["start"] for test in tests if test["start"]]
        stops = [test["stop"] for test in tests if test["stop"]]
        suites: dict[str, list[str]] = defaultdict(list)
        for test in tests:
            suites[test["suite"] or "未分类"].append(test["id"])
        return {
            "available": bool(tests),
            "summary": {
                "total": len(tests),
                "passed": status_counts["passed"],
                "failed": status_counts["failed"],
                "broken": status_counts["broken"],
                "skipped": status_counts["skipped"],
                "unknown": status_counts["unknown"],
                "start": min(starts) if starts else None,
                "stop": max(stops) if stops else None,
                "duration_ms": (max(stops) - min(starts)) if starts and stops else 0,
            },
            "suites": [{"name": name, "case_ids": ids, "count": len(ids)} for name, ids in sorted(suites.items())],
            "tests": tests,
        }

    def _normalize_result(self, result: dict, fixtures: dict) -> dict:
        labels: dict[str, list[str]] = defaultdict(list)
        for label in result.get("labels", []):
            labels[str(label.get("name", ""))].append(str(label.get("value", "")))
        start, stop = result.get("start"), result.get("stop")
        return {
            "id": result.get("uuid", ""),
            "history_id": result.get("historyId", ""),
            "name": result.get("name", "未命名用例"),
            "full_name": result.get("fullName", ""),
            "status": result.get("status", "unknown"),
            "status_details": {
                "message": _scrub(result.get("statusDetails", {}).get("message", "")),
                "trace": _scrub(result.get("statusDetails", {}).get("trace", "")),
            },
            "description": _scrub(result.get("description", "")),
            "start": start,
            "stop": stop,
            "duration_ms": max(0, stop - start) if isinstance(start, int) and isinstance(stop, int) else 0,
            "suite": self._first(labels, "suite"),
            "parent_suite": self._first(labels, "parentSuite"),
            "epic": self._first(labels, "epic"),
            "feature": self._first(labels, "feature"),
            "story": self._first(labels, "story"),
            "severity": self._first(labels, "severity"),
            "tags": labels.get("tag", []),
            "labels": dict(labels),
            "parameters": [
                {"name": item.get("name", ""), "value": _scrub(str(item.get("value", "")))}
                for item in result.get("parameters", [])
            ],
            "links": result.get("links", []),
            "steps": self._normalize_steps(result.get("steps", [])),
            "fixtures": fixtures or {"befores": [], "afters": []},
            "attachments": self._normalize_attachments(result.get("attachments", [])),
        }

    def _normalize_steps(self, steps: list[dict]) -> list[dict]:
        return [{
            "name": step.get("name", "未命名步骤"),
            "status": step.get("status", "unknown"),
            "duration_ms": max(0, step.get("stop", 0) - step.get("start", 0)),
            "status_details": {
                "message": _scrub(step.get("statusDetails", {}).get("message", "")),
                "trace": _scrub(step.get("statusDetails", {}).get("trace", "")),
            },
            "parameters": [
                {"name": item.get("name", ""), "value": _scrub(str(item.get("value", "")))}
                for item in step.get("parameters", [])
            ],
            "attachments": self._normalize_attachments(step.get("attachments", [])),
            "steps": self._normalize_steps(step.get("steps", [])),
        } for step in steps]

    def _normalize_attachments(self, attachments: list[dict]) -> list[dict]:
        normalized = []
        for item in attachments:
            source = Path(str(item.get("source", ""))).name
            path = (self.results_dir / source).resolve()
            if not source or not path.is_relative_to(self.results_dir) or not path.is_file():
                continue
            media_type = item.get("type", "application/octet-stream")
            content = ""
            if media_type in _TEXT_TYPES and path.stat().st_size <= 256_000:
                content = _scrub(path.read_text(encoding="utf-8", errors="replace"))
            normalized.append({
                "name": item.get("name", source),
                "source": f"allure-results/{source}",
                "type": media_type,
                "size": path.stat().st_size,
                "content": content,
                "preview": media_type.startswith("image/") or media_type in _TEXT_TYPES,
            })
        return normalized

    def _load_documents(self, pattern: str) -> list[dict]:
        if not self.results_dir.is_dir():
            return []
        documents = []
        for path in self.results_dir.glob(pattern):
            try:
                documents.append(json.loads(path.read_text(encoding="utf-8")))
            except (OSError, json.JSONDecodeError):
                continue
        return documents

    @staticmethod
    def _first(labels: dict[str, list[str]], name: str) -> str:
        return labels.get(name, [""])[0]

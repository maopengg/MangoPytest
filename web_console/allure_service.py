"""读取 Allure 原始结果，生成前端可直接消费的结构化数据。"""

from __future__ import annotations

from collections import Counter, defaultdict
import json
from pathlib import Path
import re
from typing import Any


_TEXT_TYPES = {"text/plain", "application/json", "text/csv", "text/html", "application/xml", "text/xml"}


def _scrub(value: str) -> str:
    """Keep local execution evidence verbatim for debugging."""
    return value


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
        normalized_steps = self._normalize_steps(result.get("steps", []))
        normalized_attachments = self._normalize_attachments(result.get("attachments", []))
        normalized_fixtures = fixtures or {"befores": [], "afters": []}
        normalized = {
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
            "feature": self._first(labels, "feature") or self._fallback_feature(result, labels),
            "story": self._first(labels, "story"),
            "severity": self._first(labels, "severity"),
            "tags": labels.get("tag", []),
            "labels": dict(labels),
            "parameters": [
                {"name": item.get("name", ""), "value": _scrub(str(item.get("value", "")))}
                for item in result.get("parameters", [])
            ],
            "links": result.get("links", []),
            "steps": normalized_steps,
            "fixtures": normalized_fixtures,
            "attachments": normalized_attachments,
        }
        normalized["evidence"] = self._extract_evidence(
            normalized_attachments, normalized_steps, normalized_fixtures
        )
        title_match = re.match(r"^([A-Za-z][A-Za-z0-9_-]*-\d+)\b", normalized["name"])
        for attachment in normalized["evidence"]["case"]:
            data = attachment.get("data")
            if isinstance(data, dict):
                data["display_name"] = normalized["name"]
                if not data.get("case_id") and title_match:
                    data["case_id"] = title_match.group(1)
        return normalized

    @classmethod
    def _fallback_feature(cls, result: dict, labels: dict[str, list[str]]) -> str:
        """Give legacy/unannotated results a stable module-level business group."""
        full_name = str(result.get("fullName", "")).split("#", 1)[0]
        candidates = [cls._first(labels, "suite"), full_name.rsplit(".", 1)[-1]]
        acronyms = {"api", "bdd", "grpc", "http", "mcp", "sse", "ui", "websocket"}
        for candidate in candidates:
            value = re.sub(r"^test_", "", candidate or "").strip("_-. ")
            if not value or value in {"test", "tests"}:
                continue
            words = re.split(r"[_\-\s]+", value)
            return " ".join(word.upper() if word.lower() in acronyms else word.title() for word in words)
        return "其他用例"

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
            data = None
            if media_type == "application/json" and content:
                try:
                    data = json.loads(content)
                except json.JSONDecodeError:
                    pass
            normalized.append({
                "name": item.get("name", source),
                "source": f"allure-results/{source}",
                "type": media_type,
                "size": path.stat().st_size,
                "content": content,
                "data": data,
                "preview": media_type.startswith("image/") or media_type in _TEXT_TYPES,
            })
        return normalized

    @staticmethod
    def _extract_evidence(attachments: list[dict], steps: list[dict], fixtures: dict) -> dict[str, list[dict]]:
        evidence: dict[str, list[dict]] = {
            "case": [], "data": [], "requests": [], "responses": [],
            "operations": [], "logs": [], "screenshots": [], "lineage": [],
        }

        def add(items: list[dict], *, context: str = "", phase: str = "") -> None:
            for attachment in items:
                evidence_item = {
                    **attachment,
                    "context": context,
                    "phase": phase,
                }
                name = str(attachment.get("name", ""))
                lowered = name.lower()
                if name == "Case 信息":
                    evidence["case"].append(evidence_item)
                elif name == "测试数据":
                    evidence["data"].append(evidence_item)
                elif name == "数据血缘":
                    evidence["lineage"].append(evidence_item)
                elif "请求信息" in name:
                    evidence["requests"].append(evidence_item)
                elif "响应信息" in name:
                    evidence["responses"].append(evidence_item)
                elif name in {"操作信息", "操作结果"}:
                    evidence["operations"].append(evidence_item)
                elif "截图" in name or attachment.get("type", "").startswith("image/"):
                    evidence["screenshots"].append(evidence_item)
                elif any(word in lowered for word in ("log", "stdout", "stderr")):
                    evidence["logs"].append(evidence_item)

        def walk(items: list[dict], *, phase: str = "") -> None:
            for step in items:
                add(step.get("attachments", []), context=step.get("name", ""), phase=phase)
                walk(step.get("steps", []), phase=phase)

        add(attachments)
        walk(steps)
        walk(fixtures.get("befores", []), phase="前置")
        walk(fixtures.get("afters", []), phase="清理")
        log_names = {str(item.get("name", "")).strip().lower() for item in evidence["logs"]}
        if "log" in log_names and "stderr" in log_names:
            # pytest 的 captured log 经常会被日志处理器再次写入 stderr。
            # 两者同时存在时保留更适合直接阅读的 stderr，避免报告重复展示同一批日志。
            evidence["logs"] = [
                item for item in evidence["logs"]
                if str(item.get("name", "")).strip().lower() != "log"
            ]
        return evidence

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

from __future__ import annotations

from pathlib import Path
import xml.etree.ElementTree as ET

from core.execution.models import RunStatus


def status_from_exit_code(exit_code: int) -> RunStatus:
    return {0: RunStatus.PASSED, 1: RunStatus.FAILED, 2: RunStatus.INTERRUPTED}.get(exit_code, RunStatus.ERROR)


def parse_junit(path: Path) -> dict[str, int]:
    result = {"total": 0, "passed": 0, "failed": 0, "errors": 0, "skipped": 0}
    if not path.is_file():
        return result
    root = ET.parse(path).getroot()
    suites = [root] if root.tag == "testsuite" else list(root.findall("testsuite"))
    for suite in suites:
        result["total"] += int(suite.attrib.get("tests", 0))
        result["failed"] += int(suite.attrib.get("failures", 0))
        result["errors"] += int(suite.attrib.get("errors", 0))
        result["skipped"] += int(suite.attrib.get("skipped", 0))
    result["passed"] = max(0, result["total"] - result["failed"] - result["errors"] - result["skipped"])
    return result


def parse_failures(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    failures = []
    root = ET.parse(path).getroot()
    for case in root.iter("testcase"):
        failure = case.find("failure")
        if failure is None:
            failure = case.find("error")
        if failure is None:
            continue
        failures.append({
            "name": case.attrib.get("name", ""),
            "classname": case.attrib.get("classname", ""),
            "message": failure.attrib.get("message", ""),
            "traceback": (failure.text or "").strip(),
        })
    return failures

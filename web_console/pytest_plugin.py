"""将 pytest 收集结果写成稳定的 JSON 清单。"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re


COLLECTION_SCHEMA_VERSION = 2
_CASE_ID = re.compile(r"\b([A-Za-z][A-Za-z0-9_-]*-\d+)\b")


def _callspec_params(item) -> dict:
    callspec = getattr(item, "callspec", None)
    params = getattr(callspec, "params", {})
    return params if isinstance(params, dict) else {}


def _display_name(item) -> str:
    """读取 Allure 标题，并尽可能渲染 pytest 参数。"""
    value = getattr(getattr(item, "obj", None), "__allure_display_name__", "")
    if not value:
        return ""
    params = _callspec_params(item)
    try:
        return str(value).format(**params)
    except (KeyError, IndexError, ValueError):
        return str(value)


def _find_case_id(*values: object) -> str:
    for value in values:
        matched = _CASE_ID.search(str(value or ""))
        if matched:
            return matched.group(1)
    return ""


def _bdd_source(item, root: Path, item_path: Path) -> tuple[Path, int, str] | None:
    scenario = getattr(getattr(item, "obj", None), "__scenario__", None)
    feature = getattr(scenario, "feature", None)
    filename = getattr(feature, "filename", "")
    if not scenario or not filename:
        return None
    feature_path = Path(str(filename))
    if not feature_path.is_absolute():
        module_relative = (item_path.parent / feature_path).resolve()
        feature_path = module_relative if module_relative.is_file() else (root / feature_path).resolve()
    else:
        feature_path = feature_path.resolve()
    if not feature_path.is_relative_to(root) or not feature_path.is_file():
        return None
    rendered = scenario
    example = _callspec_params(item).get("_pytest_bdd_example")
    if isinstance(example, dict) and hasattr(scenario, "render"):
        rendered = scenario.render(example)
    return (
        feature_path,
        int(getattr(rendered, "line_number", getattr(scenario, "line_number", 1))),
        str(getattr(rendered, "name", getattr(scenario, "name", item.name))),
    )


def pytest_addoption(parser) -> None:
    group = parser.getgroup("mango-web-console")
    group.addoption("--mango-collect-manifest", action="store", default="")


def pytest_collection_finish(session) -> None:
    destination = session.config.getoption("--mango-collect-manifest")
    if not destination:
        return
    cases = []
    root = Path(str(session.config.rootpath)).resolve()
    for item in session.items:
        item_path = Path(str(item.path)).resolve()
        if not item_path.is_relative_to(root):
            continue
        node_id = item.nodeid
        case_id = ""
        for marker in item.iter_markers():
            if marker.name in {"case_id", "case"} and marker.args:
                case_id = str(marker.args[0])
                break
        source = _bdd_source(item, root, item_path)
        source_path, source_line, source_name = source or (
            item_path, int(item.location[1]) + 1, item.name
        )
        display_name = _display_name(item)
        if not source and display_name:
            source_name = display_name
        if not case_id:
            params = _callspec_params(item)
            case_id = _find_case_id(
                source_name,
                display_name,
                item.name,
                getattr(getattr(item, "callspec", None), "id", ""),
                *params.values(),
            )
        cases.append({
            "id": hashlib.sha256(node_id.encode()).hexdigest()[:20],
            "node_id": node_id,
            "file": source_path.relative_to(root).as_posix(),
            "test_file": item_path.relative_to(root).as_posix(),
            "line": source_line,
            "name": source_name,
            "markers": sorted({marker.name for marker in item.iter_markers()}),
            "case_id": case_id,
            "source_type": "feature" if source else "python",
        })
    path = Path(destination)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({
        "schema_version": COLLECTION_SCHEMA_VERSION,
        "root": str(root),
        "count": len(cases),
        "cases": cases,
    }, ensure_ascii=False), encoding="utf-8")

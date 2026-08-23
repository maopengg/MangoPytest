"""将 pytest 收集结果写成稳定的 JSON 清单。"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


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
        cases.append({
            "id": hashlib.sha256(node_id.encode()).hexdigest()[:20],
            "node_id": node_id,
            "file": item_path.relative_to(root).as_posix(),
            "line": int(item.location[1]) + 1,
            "name": item.name,
            "markers": sorted({marker.name for marker in item.iter_markers()}),
            "case_id": case_id,
        })
    path = Path(destination)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"root": str(root), "count": len(cases), "cases": cases}, ensure_ascii=False), encoding="utf-8")

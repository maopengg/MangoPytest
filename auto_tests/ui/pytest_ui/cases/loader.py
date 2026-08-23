"""加载 pytest_ui 自己维护的 JSON 用例。"""

import json
from pathlib import Path

from .models import ElementCase, InventoryCase, OperationCase
from auto_tests.ui.pytest_ui.elements import elements

CASE_FILE = Path(__file__).resolve().parents[1] / "data" / "cases.json"
_data = json.loads(CASE_FILE.read_text(encoding="utf-8"))

OPERATION_CASES = tuple(OperationCase(**item) for item in _data["operations"])
ELEMENT_CASES = tuple(ElementCase(**item) for item in _data["elements"])
INVENTORY_CASES = tuple(InventoryCase(**item) for item in _data["inventory"])

def _validate_unique(cases, label: str) -> None:
    if not cases:
        raise ValueError(f"pytest_ui {label}用例不能为空")
    case_ids = [case.case_id for case in cases]
    if len(case_ids) != len(set(case_ids)):
        raise ValueError(f"pytest_ui {label}用例 ID 存在重复")


def _validate_element_references() -> None:
    known = {definition.name for definition in elements.all_local()}
    referenced = {case.target_id for case in OPERATION_CASES}
    referenced.update(case.verify_id for case in OPERATION_CASES if case.verify_id)
    referenced.update(case.element_id for case in ELEMENT_CASES)
    referenced.update(case.element_id for case in INVENTORY_CASES)
    referenced.update(
        case.params["target_element_id"]
        for case in OPERATION_CASES
        if "target_element_id" in case.params
    )
    missing = referenced.difference(known)
    if missing:
        raise ValueError(f"pytest_ui 用例引用了不存在的元素：{sorted(missing)}")
    inventory = {case.element_id for case in INVENTORY_CASES}
    if inventory != known:
        raise ValueError("pytest_ui 元素契约清单与本地 Excel 不一致")


_validate_unique(OPERATION_CASES, "操作能力")
_validate_unique(ELEMENT_CASES, "交互元素")
_validate_unique(INVENTORY_CASES, "元素契约")
_validate_element_references()

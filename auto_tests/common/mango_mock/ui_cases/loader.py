"""加载并校验一个 UI Demo 的 Mango Mock 能力用例。"""

from __future__ import annotations

import json
from pathlib import Path

from core.ui import configured_element_repository

from .models import ElementCase, InventoryCase, OperationCase


def load_ui_capability_cases(
    *,
    case_file: Path,
    settings,
    project_label: str,
    inventory_prefix: str,
) -> tuple[
    tuple[OperationCase, ...],
    tuple[ElementCase, ...],
    tuple[InventoryCase, ...],
]:
    data = json.loads(case_file.read_text(encoding="utf-8"))
    operations = tuple(OperationCase(**item) for item in data["operations"])
    elements = tuple(ElementCase(**item) for item in data["elements"])
    inventory = tuple(
        InventoryCase(case_prefix=inventory_prefix, **item)
        for item in data["inventory"]
    )
    _validate_unique(operations, project_label, "操作能力")
    _validate_unique(elements, project_label, "交互元素")
    _validate_unique(inventory, project_label, "元素契约")
    _validate_element_references(
        operations=operations,
        elements=elements,
        inventory=inventory,
        settings=settings,
        project_label=project_label,
    )
    return operations, elements, inventory


def _validate_unique(cases, project_label: str, label: str) -> None:
    if not cases:
        raise ValueError(f"{project_label} {label}用例不能为空")
    case_ids = [case.case_id for case in cases]
    if len(case_ids) != len(set(case_ids)):
        raise ValueError(f"{project_label} {label}用例 ID 存在重复")


def _validate_element_references(
    *,
    operations,
    elements,
    inventory,
    settings,
    project_label: str,
) -> None:
    repository = configured_element_repository(settings)
    known = {definition.name for definition in repository.all()}
    referenced = {case.target_id for case in operations}
    referenced.update(case.verify_id for case in operations if case.verify_id)
    referenced.update(case.element_id for case in elements)
    referenced.update(case.element_id for case in inventory)
    referenced.update(
        case.params["target_element_id"]
        for case in operations
        if "target_element_id" in case.params
    )
    missing = referenced.difference(known)
    if missing:
        raise ValueError(
            f"{project_label} 用例引用了不存在的元素：{sorted(missing)}"
        )
    if {case.element_id for case in inventory} != known:
        raise ValueError(f"{project_label} 元素契约清单与元素源不一致")

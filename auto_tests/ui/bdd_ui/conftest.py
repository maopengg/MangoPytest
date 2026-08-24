"""新版 bdd_ui 只注册本项目独立 Steps、Fixtures 与报告元数据。"""

import re

from core.execution import apply_case_metadata
from auto_tests.common.mango_mock.ui_cases import (
    MANGO_MOCK_UI_EPIC,
    apply_element_case_metadata,
    apply_inventory_case_metadata,
    apply_operation_case_metadata,
    group_element_cases,
    group_inventory_cases,
    group_operation_cases,
)

from auto_tests.ui.bdd_ui.capabilities.cases import ELEMENT_CASES, OPERATION_CASES
from auto_tests.ui.bdd_ui.capabilities.cases import INVENTORY_CASES

pytest_plugins = [
    "auto_tests.ui.bdd_ui.fixtures.bdd",
    "auto_tests.ui.bdd_ui.steps.mango_mock_steps",
    "auto_tests.ui.bdd_ui.steps.business_steps",
]

OPERATION_CATEGORY_BY_ID = {
    case.case_id: category
    for category, cases in group_operation_cases(OPERATION_CASES).items()
    for case in cases
}
ELEMENT_CATEGORY_BY_ID = {
    case.case_id: category
    for category, cases in group_element_cases(ELEMENT_CASES).items()
    for case in cases
}
INVENTORY_CATEGORY_BY_ID = {
    case.case_id: category
    for category, cases in group_inventory_cases(INVENTORY_CASES).items()
    for case in cases
}


def pytest_collection_modifyitems(items):
    """把能力矩阵的优先级转换为可选择的 pytest marks。"""
    priorities = {case.case_id: case.priority.lower() for case in OPERATION_CASES}
    risk_priority = {"高": "p0", "中": "p1", "低": "p2"}
    priorities.update(
        {case.case_id: risk_priority[case.risk] for case in ELEMENT_CASES}
    )
    for item in items:
        callspec = getattr(item, "callspec", None)
        example = callspec.params.get("_pytest_bdd_example", {}) if callspec else {}
        case_id = example.get("case_id") or (callspec.params.get("case_id") if callspec else None)
        if case_id in priorities:
            item.add_marker(priorities[case_id])


def pytest_bdd_before_scenario(request, feature, scenario):
    """把 Feature/Scenario 和参数化能力 Case 映射到统一报告层级。"""
    callspec = getattr(request.node, "callspec", None)
    example = callspec.params.get("_pytest_bdd_example", {}) if callspec else {}
    case_id = str(example.get("case_id") or (callspec.params.get("case_id") if callspec else "")).strip()
    operations = {case.case_id: case for case in OPERATION_CASES}
    elements = {case.case_id: case for case in ELEMENT_CASES}
    inventory = {case.case_id: case for case in INVENTORY_CASES}
    if case_id in operations:
        apply_operation_case_metadata(
            operations[case_id], category=OPERATION_CATEGORY_BY_ID[case_id]
        )
        return
    if case_id in elements:
        apply_element_case_metadata(
            elements[case_id], category=ELEMENT_CATEGORY_BY_ID[case_id]
        )
        return
    if case_id in inventory:
        apply_inventory_case_metadata(
            inventory[case_id], category=INVENTORY_CATEGORY_BY_ID[case_id]
        )
        return

    match = re.match(r"^([A-Z][A-Z0-9-]+-\d{3,4})\s+(.+)$", scenario.name)
    if not match:
        raise ValueError(f"BDD Scenario 缺少规范 Case ID：{scenario.name}")
    apply_case_metadata(
        case_id=match.group(1),
        title=match.group(2),
        epic=MANGO_MOCK_UI_EPIC,
        feature=feature.name,
    )

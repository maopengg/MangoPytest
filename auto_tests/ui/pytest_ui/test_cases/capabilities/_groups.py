"""pytest UI 能力 Case 统一分组与优先级参数。"""

import pytest

from auto_tests.common.mango_mock.ui_cases import (
    group_element_cases,
    group_inventory_cases,
    group_operation_cases,
)
from auto_tests.ui.pytest_ui.capabilities.cases import ELEMENT_CASES, INVENTORY_CASES, OPERATION_CASES

ELEMENT_GROUPS = group_element_cases(ELEMENT_CASES)
INVENTORY_GROUPS = group_inventory_cases(INVENTORY_CASES)
OPERATION_GROUPS = group_operation_cases(OPERATION_CASES)


def operation_parameters(category):
    return [pytest.param(case, id=case.case_id, marks=getattr(pytest.mark, case.priority.lower())) for case in OPERATION_GROUPS[category]]


def element_parameters(category):
    risk_marks = {"高": pytest.mark.p0, "中": pytest.mark.p1, "低": pytest.mark.p2}
    return [pytest.param(case, id=case.case_id, marks=risk_marks[case.risk]) for case in ELEMENT_GROUPS[category]]

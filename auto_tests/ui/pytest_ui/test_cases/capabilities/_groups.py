"""pytest UI 能力 Case 统一分组与优先级参数。"""

import pytest

from auto_tests.common.mango_mock.ui_cases import (
    group_element_cases,
    group_inventory_cases,
    group_operation_cases,
    is_ai_heal_case,
)
from auto_tests.ui.pytest_ui.capabilities.cases import ELEMENT_CASES, INVENTORY_CASES, OPERATION_CASES

ELEMENT_GROUPS = group_element_cases(ELEMENT_CASES)
INVENTORY_GROUPS = group_inventory_cases(INVENTORY_CASES)
OPERATION_GROUPS = group_operation_cases(OPERATION_CASES)


def _marks(case, *marks):
    """优先级/风险标记之外，为元素自愈靶场用例追加 ``ai_heal`` 标记。"""

    extra = (pytest.mark.ai_heal,) if is_ai_heal_case(case) else ()
    return (*marks, *extra)


def operation_parameters(category):
    return [
        pytest.param(
            case,
            id=case.case_id,
            marks=_marks(case, getattr(pytest.mark, case.priority.lower())),
        )
        for case in OPERATION_GROUPS[category]
    ]


def element_parameters(category):
    risk_marks = {"高": pytest.mark.p0, "中": pytest.mark.p1, "低": pytest.mark.p2}
    return [
        pytest.param(case, id=case.case_id, marks=_marks(case, risk_marks[case.risk]))
        for case in ELEMENT_GROUPS[category]
    ]

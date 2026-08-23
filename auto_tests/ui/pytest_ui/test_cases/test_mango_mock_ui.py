"""pytest 原生参数化方式覆盖新版 Mango Mock UI。"""

import allure
import pytest

from auto_tests.ui.pytest_ui.cases import (
    ELEMENT_CASES,
    INVENTORY_CASES,
    OPERATION_CASES,
)
from auto_tests.ui.pytest_ui.capabilities import PytestUICasePage

pytestmark = [pytest.mark.ui, pytest.mark.positive, pytest.mark.capability]


def _operation_parameters():
    return [
        pytest.param(case, id=case.case_id, marks=getattr(pytest.mark, case.priority.lower()))
        for case in OPERATION_CASES
    ]


def _element_parameters():
    risk_marks = {"高": pytest.mark.p0, "中": pytest.mark.p1, "低": pytest.mark.p2}
    return [
        pytest.param(case, id=case.case_id, marks=risk_marks[case.risk])
        for case in ELEMENT_CASES
    ]


@allure.feature("pytest mangoautomation 操作覆盖")
@pytest.mark.parametrize("operation_case", _operation_parameters())
def test_mangoautomation_operation(base_data, operation_case):
    page = PytestUICasePage(base_data)
    page.execute_operation(operation_case)


@allure.feature("pytest UI 控件交互")
@pytest.mark.parametrize("element_case", _element_parameters())
def test_interactive_element(base_data, ui_data_factory, element_case):
    page = PytestUICasePage(base_data, ui_data_factory)
    try:
        page.execute_element(element_case)
    finally:
        page.cleanup_run()


@allure.feature("pytest UI 元素定位")
@pytest.mark.parametrize("inventory_case", INVENTORY_CASES, ids=lambda case: case.case_id)
def test_all_elements(base_data, inventory_case):
    page = PytestUICasePage(base_data)
    page.verify_inventory(inventory_case)

"""控件状态逐一操作。"""

import pytest

from auto_tests.common.mango_mock.ui_cases import apply_element_case_metadata
from auto_tests.ui.simple_ui.abstract.excel_case_page import ExcelCasePage
from auto_tests.ui.simple_ui.test_cases.capabilities._groups import ELEMENT_GROUPS

pytestmark = [pytest.mark.integration, pytest.mark.positive]


@pytest.mark.parametrize("element_case", ELEMENT_GROUPS["states"], ids=lambda case: case.case_id)
def test_state_controls(base_data, element_case):
    apply_element_case_metadata(element_case, category="states")
    page = ExcelCasePage(base_data)
    try:
        page.execute_element(element_case)
    finally:
        page.cleanup_run()

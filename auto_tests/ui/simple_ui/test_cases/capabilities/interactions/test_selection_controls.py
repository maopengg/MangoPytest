"""选择控件逐一操作。"""

import pytest

from auto_tests.common.mango_mock.ui_cases import apply_element_case_metadata
from auto_tests.ui.simple_ui.abstract.excel_case_page import ExcelCasePage
from auto_tests.ui.simple_ui.test_cases.capabilities._groups import ELEMENT_GROUPS

pytestmark = [pytest.mark.integration, pytest.mark.positive]


@pytest.mark.parametrize("element_case", ELEMENT_GROUPS["selections"], ids=lambda case: case.case_id)
def test_selection_controls(base_data, element_case):
    apply_element_case_metadata(element_case, category="selections")
    page = ExcelCasePage(base_data)
    try:
        page.execute_element(element_case)
    finally:
        page.cleanup_run()

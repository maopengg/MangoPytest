"""鼠标拖拽与滚动能力。"""

import pytest

from auto_tests.common.mango_mock.ui_cases import apply_operation_case_metadata
from auto_tests.ui.simple_ui.abstract.excel_case_page import ExcelCasePage
from auto_tests.ui.simple_ui.test_cases.capabilities._groups import OPERATION_GROUPS

pytestmark = [pytest.mark.integration, pytest.mark.positive]


@pytest.mark.parametrize("operation_case", OPERATION_GROUPS["mouse_drag_scroll"], ids=lambda case: case.case_id)
def test_mouse_drag_scroll_operations(base_data, operation_case):
    apply_operation_case_metadata(operation_case, category="mouse_drag_scroll")
    ExcelCasePage(base_data).execute_operation(operation_case)

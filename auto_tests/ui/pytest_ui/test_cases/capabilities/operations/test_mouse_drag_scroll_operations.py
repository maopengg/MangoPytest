"""鼠标拖拽与滚动能力。"""

import pytest

from auto_tests.common.mango_mock.ui_cases import apply_operation_case_metadata
from auto_tests.ui.pytest_ui.capabilities import PytestUICasePage
from auto_tests.ui.pytest_ui.test_cases.capabilities._groups import operation_parameters

pytestmark = [pytest.mark.ui, pytest.mark.positive, pytest.mark.capability]


@pytest.mark.parametrize("operation_case", operation_parameters("mouse_drag_scroll"))
def test_mouse_drag_scroll_operations(base_data, operation_case):
    apply_operation_case_metadata(operation_case, category="mouse_drag_scroll")
    PytestUICasePage(base_data).execute_operation(operation_case)

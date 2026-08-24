"""浏览器与页签导航能力。"""

import pytest

from auto_tests.common.mango_mock.ui_cases import apply_operation_case_metadata
from auto_tests.ui.pytest_ui.capabilities import PytestUICasePage
from auto_tests.ui.pytest_ui.test_cases.capabilities._groups import operation_parameters

pytestmark = [pytest.mark.ui, pytest.mark.positive, pytest.mark.capability]


@pytest.mark.parametrize("operation_case", operation_parameters("browser_navigation"))
def test_browser_navigation_operations(base_data, operation_case):
    apply_operation_case_metadata(operation_case, category="browser_navigation")
    PytestUICasePage(base_data).execute_operation(operation_case)

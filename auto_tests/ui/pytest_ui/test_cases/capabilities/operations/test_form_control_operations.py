"""表单控件操作能力。"""

import pytest

from auto_tests.common.mango_mock.ui_cases import apply_operation_case_metadata
from auto_tests.ui.pytest_ui.capabilities import PytestUICasePage
from auto_tests.ui.pytest_ui.test_cases.capabilities._groups import operation_parameters

pytestmark = [pytest.mark.ui, pytest.mark.positive, pytest.mark.capability]


@pytest.mark.parametrize("operation_case", operation_parameters("form_controls"))
def test_form_control_operations(base_data, operation_case):
    apply_operation_case_metadata(operation_case, category="form_controls")
    PytestUICasePage(base_data).execute_operation(operation_case)

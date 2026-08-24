"""表单控件操作 Feature 一对一绑定。"""

import pytest
from pytest_bdd import scenario

from auto_tests.ui.bdd_ui.test_cases.capabilities._groups import OPERATION_GROUPS

pytestmark = [pytest.mark.ui, pytest.mark.positive, pytest.mark.capability]


@pytest.mark.parametrize("case_id", [case.case_id for case in OPERATION_GROUPS["form_controls"]])
@scenario("../../../features/capabilities/operations/form_control_operations.feature", "验证表单控件操作能力")
def test_form_control_operations(case_id):
    pass

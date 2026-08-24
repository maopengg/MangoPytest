"""浏览器上下文 Feature 一对一绑定。"""

import pytest
from pytest_bdd import scenario

from auto_tests.ui.bdd_ui.test_cases.capabilities._groups import OPERATION_GROUPS

pytestmark = [pytest.mark.ui, pytest.mark.positive, pytest.mark.capability]


@pytest.mark.parametrize("case_id", [case.case_id for case in OPERATION_GROUPS["browser_context"]])
@scenario("../../../features/capabilities/operations/browser_context_operations.feature", "验证浏览器上下文能力")
def test_browser_context_operations(case_id):
    pass

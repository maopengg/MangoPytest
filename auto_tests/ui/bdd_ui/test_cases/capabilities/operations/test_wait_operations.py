"""等待机制 Feature 一对一绑定。"""

import pytest
from pytest_bdd import scenario

from auto_tests.ui.bdd_ui.test_cases.capabilities._groups import OPERATION_GROUPS

pytestmark = [pytest.mark.ui, pytest.mark.positive, pytest.mark.capability]


@pytest.mark.parametrize("case_id", [case.case_id for case in OPERATION_GROUPS["waits"]])
@scenario("../../../features/capabilities/operations/wait_operations.feature", "验证等待机制能力")
def test_wait_operations(case_id):
    pass

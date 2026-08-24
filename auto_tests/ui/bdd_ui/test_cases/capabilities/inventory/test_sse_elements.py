"""SSE 元素 Feature 一对一绑定。"""

import pytest
from pytest_bdd import scenario

from auto_tests.ui.bdd_ui.test_cases.capabilities._groups import INVENTORY_GROUPS

pytestmark = [pytest.mark.ui, pytest.mark.positive, pytest.mark.capability]


@pytest.mark.parametrize("case_id", [case.case_id for case in INVENTORY_GROUPS["ssePage"]])
@scenario("../../../features/capabilities/inventory/sse_elements.feature", "验证SSE 元素能力")
def test_sse_elements(case_id):
    pass

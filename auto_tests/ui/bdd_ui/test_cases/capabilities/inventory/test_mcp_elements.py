"""MCP 元素 Feature 一对一绑定。"""

import pytest
from pytest_bdd import scenario

from auto_tests.ui.bdd_ui.test_cases.capabilities._groups import INVENTORY_GROUPS

pytestmark = [pytest.mark.ui, pytest.mark.positive, pytest.mark.capability]


@pytest.mark.parametrize("case_id", [case.case_id for case in INVENTORY_GROUPS["mcpPage"]])
@scenario("../../../features/capabilities/inventory/mcp_elements.feature", "验证MCP 元素能力")
def test_mcp_elements(case_id):
    pass

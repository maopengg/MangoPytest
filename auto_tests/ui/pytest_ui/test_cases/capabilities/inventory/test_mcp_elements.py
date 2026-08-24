"""MCP 元素定位。"""

import pytest

from auto_tests.common.mango_mock.ui_cases import apply_inventory_case_metadata
from auto_tests.ui.pytest_ui.capabilities import PytestUICasePage
from auto_tests.ui.pytest_ui.test_cases.capabilities._groups import INVENTORY_GROUPS

pytestmark = [pytest.mark.ui, pytest.mark.positive, pytest.mark.capability]


@pytest.mark.parametrize("inventory_case", INVENTORY_GROUPS["mcpPage"], ids=lambda case: case.case_id)
def test_mcp_elements(base_data, inventory_case):
    apply_inventory_case_metadata(inventory_case, category="mcpPage")
    PytestUICasePage(base_data).verify_inventory(inventory_case)

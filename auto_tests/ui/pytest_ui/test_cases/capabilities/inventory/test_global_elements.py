"""全局导航元素定位。"""

import pytest

from auto_tests.common.mango_mock.ui_cases import apply_inventory_case_metadata
from auto_tests.ui.pytest_ui.capabilities import PytestUICasePage
from auto_tests.ui.pytest_ui.test_cases.capabilities._groups import INVENTORY_GROUPS

pytestmark = [pytest.mark.ui, pytest.mark.positive, pytest.mark.capability]


@pytest.mark.parametrize("inventory_case", INVENTORY_GROUPS["global"], ids=lambda case: case.case_id)
def test_global_elements(base_data, inventory_case):
    apply_inventory_case_metadata(inventory_case, category="global")
    PytestUICasePage(base_data).verify_inventory(inventory_case)

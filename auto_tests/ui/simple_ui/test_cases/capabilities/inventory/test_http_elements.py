"""HTTP 业务元素定位。"""

import pytest

from auto_tests.common.mango_mock.ui_cases import apply_inventory_case_metadata
from auto_tests.ui.simple_ui.abstract.excel_case_page import ExcelCasePage
from auto_tests.ui.simple_ui.test_cases.capabilities._groups import INVENTORY_GROUPS

pytestmark = [pytest.mark.integration, pytest.mark.positive]


@pytest.mark.parametrize("inventory_case", INVENTORY_GROUPS["httpPage"], ids=lambda case: case.case_id)
def test_http_elements(base_data, inventory_case):
    apply_inventory_case_metadata(inventory_case, category="httpPage")
    ExcelCasePage(base_data).verify_inventory(inventory_case)

"""BDD UI 能力 Case 统一分组。"""

from auto_tests.common.mango_mock.ui_cases import (
    group_element_cases,
    group_inventory_cases,
    group_operation_cases,
)
from auto_tests.ui.bdd_ui.capabilities.cases import ELEMENT_CASES, INVENTORY_CASES, OPERATION_CASES

ELEMENT_GROUPS = group_element_cases(ELEMENT_CASES)
INVENTORY_GROUPS = group_inventory_cases(INVENTORY_CASES)
OPERATION_GROUPS = group_operation_cases(OPERATION_CASES)

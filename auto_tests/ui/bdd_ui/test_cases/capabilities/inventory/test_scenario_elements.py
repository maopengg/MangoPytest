"""场景编排元素 Feature 一对一绑定。"""

import pytest
from pytest_bdd import scenario

from auto_tests.ui.bdd_ui.test_cases.capabilities._groups import INVENTORY_GROUPS

pytestmark = [pytest.mark.ui, pytest.mark.positive, pytest.mark.capability]


@pytest.mark.parametrize("case_id", [case.case_id for case in INVENTORY_GROUPS["scenariosPage"]])
@scenario("../../../features/capabilities/inventory/scenario_elements.feature", "验证场景编排元素能力")
def test_scenario_elements(case_id):
    pass

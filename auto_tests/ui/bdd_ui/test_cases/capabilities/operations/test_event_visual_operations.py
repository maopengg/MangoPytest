"""事件与视觉辅助 Feature 一对一绑定。"""

import pytest
from pytest_bdd import scenario

from auto_tests.ui.bdd_ui.test_cases.capabilities._groups import OPERATION_GROUPS

pytestmark = [pytest.mark.ui, pytest.mark.positive, pytest.mark.capability]


@pytest.mark.parametrize("case_id", [case.case_id for case in OPERATION_GROUPS["events_visuals"]])
@scenario("../../../features/capabilities/operations/event_visual_operations.feature", "验证事件与视觉辅助能力")
def test_event_visual_operations(case_id):
    pass

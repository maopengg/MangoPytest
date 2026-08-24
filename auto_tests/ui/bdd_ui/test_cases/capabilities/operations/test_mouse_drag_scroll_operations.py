"""鼠标拖拽与滚动 Feature 一对一绑定。"""

import pytest
from pytest_bdd import scenario

from auto_tests.ui.bdd_ui.test_cases.capabilities._groups import OPERATION_GROUPS

pytestmark = [pytest.mark.ui, pytest.mark.positive, pytest.mark.capability]


@pytest.mark.parametrize("case_id", [case.case_id for case in OPERATION_GROUPS["mouse_drag_scroll"]])
@scenario("../../../features/capabilities/operations/mouse_drag_scroll_operations.feature", "验证鼠标拖拽与滚动能力")
def test_mouse_drag_scroll_operations(case_id):
    pass

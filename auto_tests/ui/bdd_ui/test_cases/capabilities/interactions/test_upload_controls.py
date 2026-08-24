"""文件上传控件 Feature 一对一绑定。"""

import pytest
from pytest_bdd import scenario

from auto_tests.ui.bdd_ui.test_cases.capabilities._groups import ELEMENT_GROUPS

pytestmark = [pytest.mark.ui, pytest.mark.positive, pytest.mark.capability]


@pytest.mark.parametrize("case_id", [case.case_id for case in ELEMENT_GROUPS["uploads"]])
@scenario("../../../features/capabilities/interactions/upload_controls.feature", "验证文件上传控件能力")
def test_upload_controls(case_id):
    pass

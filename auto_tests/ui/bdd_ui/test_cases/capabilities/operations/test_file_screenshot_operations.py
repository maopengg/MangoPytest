"""文件与截图操作 Feature 一对一绑定。"""

import pytest
from pytest_bdd import scenario

from auto_tests.ui.bdd_ui.test_cases.capabilities._groups import OPERATION_GROUPS

pytestmark = [pytest.mark.ui, pytest.mark.positive, pytest.mark.capability]


@pytest.mark.parametrize("case_id", [case.case_id for case in OPERATION_GROUPS["files_screenshots"]])
@scenario("../../../features/capabilities/operations/file_screenshot_operations.feature", "验证文件与截图操作能力")
def test_file_screenshot_operations(case_id):
    pass

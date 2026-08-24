"""文件上传控件逐一操作。"""

import pytest

from auto_tests.common.mango_mock.ui_cases import apply_element_case_metadata
from auto_tests.ui.pytest_ui.capabilities import PytestUICasePage
from auto_tests.ui.pytest_ui.test_cases.capabilities._groups import element_parameters

pytestmark = [pytest.mark.ui, pytest.mark.positive, pytest.mark.capability]


@pytest.mark.parametrize("element_case", element_parameters("uploads"))
def test_upload_controls(base_data, ui_data_factory, element_case):
    apply_element_case_metadata(element_case, category="uploads")
    page = PytestUICasePage(base_data, ui_data_factory)
    try:
        page.execute_element(element_case)
    finally:
        page.cleanup_run()

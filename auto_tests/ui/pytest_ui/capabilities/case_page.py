"""pytest 项目对公共 Mango Mock UI 能力执行器的装配。"""

from pathlib import Path

from auto_tests.common.mango_mock.ui_capabilities import MangoMockUICasePage
from auto_tests.ui.pytest_ui.config import settings


class PytestUICasePage(MangoMockUICasePage):
    def __init__(self, base_data, data_factory=None):
        super().__init__(
            base_data,
            data_factory,
            settings=settings,
            run_name_prefix="AUTO_PYTEST_UI",
            mode_name="pytest",
            upload_file=str(
                Path(__file__).resolve().parents[1] / "data" / "upload.txt"
            ),
        )

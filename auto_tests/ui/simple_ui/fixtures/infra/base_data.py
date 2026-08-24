"""simple_ui Case 级 BaseData Fixture。"""

import pytest

from auto_tests.ui.simple_ui.config import settings
from core.ui import request_needs_touch, ui_base_data_session
from core.utils import log


@pytest.fixture
def base_data(web_runtime, request):
    device = "iPhone 13" if request_needs_touch(request) else None
    with ui_base_data_session(
        web_runtime=web_runtime,
        request=request,
        settings=settings,
        log=log,
        device=device,
    ) as data:
        yield data

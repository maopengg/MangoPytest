"""simple_ui Session 级同步 Web Runtime Fixture。"""

import pytest

from auto_tests.ui.simple_ui.config import settings
from core.ui import sync_web_runtime_session
from core.utils import log


@pytest.fixture(scope="session")
def web_runtime():
    with sync_web_runtime_session(settings, log) as runtime:
        yield runtime

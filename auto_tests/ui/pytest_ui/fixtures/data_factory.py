"""pytest_ui 的独立前置数据 fixtures。"""

import pytest

from auto_tests.ui.pytest_ui.config import settings
from auto_tests.ui.pytest_ui.data_factory import PytestUIDataFactory
from auto_tests.ui.pytest_ui.repositories import PytestUIRepositories


@pytest.fixture
def ui_repositories():
    repositories = PytestUIRepositories(
        settings.BASE_URL,
        timeout=settings.PAGE_LOAD_TIMEOUT,
    )
    yield repositories
    repositories.close()


@pytest.fixture
def ui_data_factory(ui_repositories):
    return PytestUIDataFactory(ui_repositories)

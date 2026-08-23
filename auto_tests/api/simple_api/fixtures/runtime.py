"""简单 API 示例使用的 pytest fixtures。"""

import pytest

from auto_tests.api.simple_api.config import settings
from auto_tests.api.simple_api.data_factory.factories import SimpleApiFactory
from auto_tests.api.simple_api.data_factory.specs import SimpleApiSpec
from auto_tests.api.simple_api.repositories.simple_api import SimpleApiRepository


@pytest.fixture
def simple_api_factory():
    return SimpleApiFactory(SimpleApiSpec())


@pytest.fixture
def simple_api_repository(simple_api_factory):
    repository = SimpleApiRepository(
        base_url=settings.BASE_URL,
        admin_token=settings.MOCK_ADMIN_TOKEN,
        entity=simple_api_factory.build(),
        timeout=settings.MOCK_TIMEOUT,
    )
    yield repository
    repository.close()

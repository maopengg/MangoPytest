"""bdd_api 的 pytest/BDD 全局配置。"""

import pytest

from auto_tests.api.bdd_api.config import settings
from auto_tests.api.bdd_api.data_factory.specs.cross_protocol import cross_protocol_spec
from auto_tests.api.bdd_api.data_factory.factories import (
    CrossProtocolFactory,
    FunctionalCaseFactory,
    ProductFactory,
)
from auto_tests.api.bdd_api.repos.cross_protocol import CrossProtocolRepository
from auto_tests.api.bdd_api.repos.functional_cases import FunctionalCaseRepository
from auto_tests.api.bdd_api.repos.products import ProductRepository
from auto_tests.api.bdd_api.steps.api.functional_case_executor import FunctionalCaseExecutor

from auto_tests.api.bdd_api.steps.common.cross_protocol import *  # noqa: F401,F403
from auto_tests.api.bdd_api.steps.auth.cross_protocol import *  # noqa: F401,F403
from auto_tests.api.bdd_api.steps.data.cross_protocol import *  # noqa: F401,F403
from auto_tests.api.bdd_api.steps.api.cross_protocol import *  # noqa: F401,F403
from auto_tests.api.bdd_api.steps.assertions.cross_protocol import *  # noqa: F401,F403
from auto_tests.api.bdd_api.steps.api.functional_cases import *  # noqa: F401,F403
from auto_tests.api.bdd_api.steps.assertions.functional_cases import *  # noqa: F401,F403
from auto_tests.api.bdd_api.steps.data.products import *  # noqa: F401,F403
from auto_tests.api.bdd_api.steps.api.products import *  # noqa: F401,F403
from auto_tests.api.bdd_api.steps.assertions.products import *  # noqa: F401,F403


@pytest.fixture
def scenario_context() -> dict:
    return {}


@pytest.fixture
def cross_protocol_repository():
    repository = CrossProtocolRepository(
        settings.BASE_URL,
        timeout=settings.MOCK_TIMEOUT,
        admin_token=settings.MOCK_ADMIN_TOKEN,
    ).start()
    yield repository
    repository.close()


@pytest.fixture
def secondary_repository():
    repository = CrossProtocolRepository(
        settings.BASE_URL,
        timeout=settings.MOCK_TIMEOUT,
        admin_token=settings.MOCK_ADMIN_TOKEN,
    ).start()
    yield repository
    repository.close()


@pytest.fixture
def cross_protocol_factory(cross_protocol_repository):
    return CrossProtocolFactory(cross_protocol_repository)


@pytest.fixture
def functional_case_repository(cross_protocol_repository):
    repository = FunctionalCaseRepository(cross_protocol_repository)
    yield repository
    repository.close()


@pytest.fixture
def functional_case_factory():
    return FunctionalCaseFactory()


@pytest.fixture
def product_factory():
    return ProductFactory()


@pytest.fixture
def product_repository(functional_case_repository):
    return ProductRepository(functional_case_repository)


@pytest.fixture
def functional_case_executor(functional_case_repository, functional_case_factory):
    return FunctionalCaseExecutor(functional_case_repository, functional_case_factory)


@pytest.fixture
def cross_protocol_entity():
    return cross_protocol_spec()


@pytest.fixture
def api_response(scenario_context):
    return scenario_context.get("api_response")


def pytest_configure(config):
    markers = {
        "smoke": "冒烟测试",
        "positive": "正向测试",
        "negative": "负向测试",
        "security": "安全测试",
        "integration": "集成测试",
        "cross_protocol": "跨协议测试",
        "websocket": "WebSocket 测试",
        "mcp": "MCP 测试",
        "grpc": "gRPC 测试",
        "sse": "SSE 测试",
        "http": "HTTP 测试",
        "webhook": "Webhook 测试",
    }
    for name, description in markers.items():
        config.addinivalue_line("markers", f"{name}: {description}")

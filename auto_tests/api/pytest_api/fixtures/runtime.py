"""pytest_api 的运行时、Repository 与 Data Factory fixtures。"""

import pytest

from auto_tests.api.pytest_api.config import settings
from auto_tests.api.pytest_api.data_factory.factories.cross_protocol_factory import (
    CrossProtocolFactory,
)
from auto_tests.api.pytest_api.data_factory.factories.demo_data_factory import (
    DemoDataFactory,
)
from auto_tests.api.pytest_api.data_factory.specs.cross_protocol import cross_protocol_spec
from auto_tests.api.pytest_api.repositories.cross_protocol import CrossProtocolRepository
from auto_tests.api.pytest_api.repositories.common import MangoMockRepository
from auto_tests.api.pytest_api.data_factory.factories.product_factory import ProductFactory
from auto_tests.api.pytest_api.repositories.products import ProductRepository
from auto_tests.api.pytest_api.services.products import ProductService
from auto_tests.api.pytest_api.services.cross_protocol import CrossProtocolService
from auto_tests.api.pytest_api.services.auth import AuthService
from auto_tests.api.pytest_api.services.claims import ClaimService
from auto_tests.api.pytest_api.services.orders import OrderService
from auto_tests.api.pytest_api.services.reviews import ReviewService
from auto_tests.api.pytest_api.services.test_runs import TestRunService
from auto_tests.api.pytest_api.services.faults import FaultService
from auto_tests.api.pytest_api.services.http_lab import HttpLabService
from auto_tests.api.pytest_api.services.webhooks import WebhookService
from auto_tests.api.pytest_api.services.grpc import GrpcService
from auto_tests.api.pytest_api.services.mcp import McpService
from auto_tests.api.pytest_api.services.sse import SseService
from auto_tests.api.pytest_api.services.websocket import WebSocketService


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
def mango_mock_repository(cross_protocol_repository):
    repository = MangoMockRepository(cross_protocol_repository)
    yield repository
    repository.close()


@pytest.fixture
def demo_data_factory():
    return DemoDataFactory()


@pytest.fixture
def assert_scenario():
    def verify(result):
        failed = result.failed_checks()
        assert not failed, f"场景检查失败: {failed}; details={result.details}"
    return verify


@pytest.fixture
def test_run_service(mango_mock_repository, demo_data_factory):
    return TestRunService(mango_mock_repository, demo_data_factory)


@pytest.fixture
def auth_service(mango_mock_repository):
    return AuthService(mango_mock_repository)


@pytest.fixture
def order_service(mango_mock_repository, demo_data_factory):
    return OrderService(mango_mock_repository, demo_data_factory)


@pytest.fixture
def claim_service(mango_mock_repository, demo_data_factory):
    return ClaimService(mango_mock_repository, demo_data_factory)


@pytest.fixture
def review_service(mango_mock_repository, demo_data_factory):
    return ReviewService(mango_mock_repository, demo_data_factory)


@pytest.fixture
def http_lab_service(mango_mock_repository, demo_data_factory):
    return HttpLabService(mango_mock_repository, demo_data_factory)


@pytest.fixture
def fault_service(mango_mock_repository, demo_data_factory):
    return FaultService(mango_mock_repository, demo_data_factory)


@pytest.fixture
def webhook_service(mango_mock_repository, demo_data_factory):
    return WebhookService(mango_mock_repository, demo_data_factory)


@pytest.fixture
def sse_service(mango_mock_repository, demo_data_factory):
    return SseService(mango_mock_repository, demo_data_factory)


@pytest.fixture
def websocket_service(mango_mock_repository, demo_data_factory):
    return WebSocketService(mango_mock_repository, demo_data_factory)


@pytest.fixture
def mcp_service(mango_mock_repository, demo_data_factory):
    return McpService(mango_mock_repository, demo_data_factory)


@pytest.fixture
def grpc_service(mango_mock_repository, demo_data_factory):
    return GrpcService(mango_mock_repository, demo_data_factory)


@pytest.fixture
def product_factory():
    return ProductFactory()


@pytest.fixture
def product_repository(mango_mock_repository):
    return ProductRepository(mango_mock_repository)


@pytest.fixture
def product_service(product_repository, product_factory):
    return ProductService(product_repository, product_factory)


@pytest.fixture
def cross_protocol_entity():
    return cross_protocol_spec()


@pytest.fixture
def cross_protocol_service(
    cross_protocol_repository, cross_protocol_factory, cross_protocol_entity
):
    return CrossProtocolService(
        cross_protocol_repository, cross_protocol_factory, cross_protocol_entity
    )


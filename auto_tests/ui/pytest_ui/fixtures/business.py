"""业务 Page Object 与 Flow Fixtures。"""

import pytest

from auto_tests.common.mango_mock.ui_business import (
    ClaimFlow,
    ClaimPage,
    OrderFlow,
    OrderPage,
    ReviewFlow,
    ReviewPage,
)
from auto_tests.ui.pytest_ui.config import settings


@pytest.fixture
def order_flow(base_data):
    return OrderFlow(OrderPage(base_data, settings))


@pytest.fixture
def claim_flow(base_data):
    return ClaimFlow(ClaimPage(base_data, settings))


@pytest.fixture
def review_flow(base_data):
    return ReviewFlow(ReviewPage(base_data, settings))

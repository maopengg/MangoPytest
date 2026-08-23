"""业务 Page Object 与 Flow Fixtures。"""

import pytest

from auto_tests.ui.pytest_ui.flows import ClaimFlow, OrderFlow, ReviewFlow
from auto_tests.ui.pytest_ui.page_object.business import ClaimPage, OrderPage, ReviewPage


@pytest.fixture
def order_flow(base_data):
    return OrderFlow(OrderPage(base_data))


@pytest.fixture
def claim_flow(base_data):
    return ClaimFlow(ClaimPage(base_data))


@pytest.fixture
def review_flow(base_data):
    return ReviewFlow(ReviewPage(base_data))

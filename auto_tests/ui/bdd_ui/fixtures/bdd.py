"""bdd_ui 浏览器、上下文和数据工厂 Fixtures。"""

import pytest

from auto_tests.common.mango_mock.repositories import MangoMockRepositories
from auto_tests.common.mango_mock.ui_business import (
    ClaimFlow,
    ClaimPage,
    OrderFlow,
    OrderPage,
    ReviewFlow,
    ReviewPage,
)
from auto_tests.ui.bdd_ui.config import settings
from auto_tests.ui.bdd_ui.contexts import (
    ClaimScenarioContext,
    OrderScenarioContext,
    ReviewScenarioContext,
)
from auto_tests.ui.bdd_ui.data_factory import BddUIDataFactory
from core.ui import (
    request_needs_touch,
    sync_web_runtime_session,
    ui_base_data_session,
)
from core.utils import log


@pytest.fixture(scope="session")
def web_runtime():
    with sync_web_runtime_session(settings, log) as runtime:
        yield runtime


@pytest.fixture
def base_data(web_runtime, request):
    touch_cases = {"UI-OP-031", "UI-EL-044"}
    device = (
        "iPhone 13"
        if request_needs_touch(request, case_ids=touch_cases)
        else None
    )
    with ui_base_data_session(
        web_runtime=web_runtime,
        request=request,
        settings=settings,
        log=log,
        device=device,
    ) as data:
        yield data


@pytest.fixture
def bdd_ui_repositories():
    repositories = MangoMockRepositories(
        settings.BASE_URL,
        timeout=settings.PAGE_LOAD_TIMEOUT,
        run_name_prefix="AUTO_BDD_UI",
    )
    yield repositories
    repositories.close()


@pytest.fixture
def bdd_ui_data_factory(bdd_ui_repositories):
    return BddUIDataFactory(bdd_ui_repositories)


@pytest.fixture
def order_flow(base_data):
    return OrderFlow(OrderPage(base_data, settings))


@pytest.fixture
def claim_flow(base_data):
    return ClaimFlow(ClaimPage(base_data, settings))


@pytest.fixture
def review_flow(base_data):
    return ReviewFlow(ReviewPage(base_data, settings))


@pytest.fixture
def scenario_context() -> dict:
    return {}


@pytest.fixture
def order_context() -> OrderScenarioContext:
    return OrderScenarioContext()


@pytest.fixture
def claim_context() -> ClaimScenarioContext:
    return ClaimScenarioContext()


@pytest.fixture
def review_context() -> ReviewScenarioContext:
    return ReviewScenarioContext()

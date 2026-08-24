"""pytest UI 场景级 Data Factory 门面。"""

import json
from typing import Any

from auto_tests.common.mango_mock.repositories import MangoMockRepositories

from .entities import ClaimData, OrderData, ReviewData, RunData
from .factories import ClaimFactory, OrderFactory, ReviewFactory
from .specs import ClaimSpec, OrderSpec, ReviewSpec


class PytestUIDataFactory:
    """组合实体 Factory，并记录当前场景创建的全部实体。"""

    def __init__(self, repository: MangoMockRepositories):
        self.repository = repository
        self.order_factory = OrderFactory(repository.orders)
        self.claim_factory = ClaimFactory(repository.claims)
        self.review_factory = ReviewFactory(repository.reviews)
        self.orders: list[OrderData] = []
        self.claims: list[ClaimData] = []
        self.reviews: list[ReviewData] = []

    @property
    def order_id(self) -> int | None:
        return self.orders[-1].id if self.orders else None

    @property
    def claim_id(self) -> int | None:
        return self.claims[-1].id if self.claims else None

    @property
    def review_id(self) -> int | None:
        return self.reviews[-1].id if self.reviews else None

    def run(self, role: str = "employee") -> RunData:
        token, user = self.repository.auth.login(role)
        return RunData(
            self.repository.run_id,
            self.repository.cleanup_token,
            token,
            user,
        )

    def create_order(self, status: str = "pending", quantity: int = 1) -> OrderData:
        entity = self.order_factory.create(OrderSpec(status=status, quantity=quantity))
        self.orders.append(entity)
        return entity

    def create_claim(
        self, amount: int = 12000, reason: str = "AUTO_PYTEST_UI 前置报销"
    ) -> ClaimData:
        entity = self.claim_factory.create(ClaimSpec(amount=amount, reason=reason))
        self.claims.append(entity)
        return entity

    def create_review(
        self,
        contract_name: str = "AUTO_PYTEST_UI 合同",
        duration_seconds: int = 5,
        expected_risk_count: int = 2,
    ) -> ReviewData:
        entity = self.review_factory.create(
            ReviewSpec(contract_name, duration_seconds, expected_risk_count)
        )
        self.reviews.append(entity)
        return entity

    def browser_state(self, role: str = "employee") -> dict[str, Any]:
        run = self.run(role)
        return {
            "runId": run.run_id,
            "cleanupToken": run.cleanup_token,
            "token": run.token,
            "user": run.user,
            "orderId": self.order_id,
            "claimId": self.claim_id,
            "reviewId": self.review_id,
        }

    def bind_browser(self, base_data, role: str = "employee") -> None:
        state = self.browser_state(role)
        encoded = json.dumps(state, ensure_ascii=False)
        init_script = (
            "localStorage.setItem('mango-mock-session', "
            f"JSON.stringify({encoded}));"
        )
        base_data.context.add_init_script(script=init_script)
        if base_data.page.url.startswith(("http://", "https://")):
            base_data.page.evaluate(
                "value => localStorage.setItem('mango-mock-session', JSON.stringify(value))",
                state,
            )
            base_data.page.reload(wait_until="domcontentloaded")

    def mark_deleted(self) -> None:
        self.repository.deleted = True

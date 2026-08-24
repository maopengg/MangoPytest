"""订单、报销和评审实体 Factory。"""

import uuid

from auto_tests.common.mango_mock.repositories import (
    ClaimRepository,
    OrderRepository,
    ReviewRepository,
)

from ..entities import ClaimData, OrderData, ReviewData
from ..specs import ClaimSpec, OrderSpec, ReviewSpec


class OrderFactory:
    def __init__(self, repository: OrderRepository):
        self.repository = repository

    def create(self, spec: OrderSpec | None = None) -> OrderData:
        current = spec or OrderSpec()
        products = self.repository.products()
        if not products:
            raise AssertionError("Mango Mock 没有可用于创建订单的商品")
        raw = self.repository.create(
            products[0]["id"],
            current.quantity,
            f"AUTO_BDD_UI_{uuid.uuid4().hex[:12]}",
        )
        if current.status in {"paid", "refunded"}:
            raw = {**raw, **self.repository.pay(raw["id"])}
        if current.status == "refunded":
            raw = {**raw, **self.repository.refund(raw["id"])}
        return OrderData(raw["id"], raw["status"], raw)


class ClaimFactory:
    def __init__(self, repository: ClaimRepository):
        self.repository = repository

    def create(self, spec: ClaimSpec | None = None) -> ClaimData:
        current = spec or ClaimSpec()
        raw = self.repository.create(current.amount, current.reason)
        return ClaimData(raw["id"], raw["status"], raw)


class ReviewFactory:
    def __init__(self, repository: ReviewRepository):
        self.repository = repository

    def create(self, spec: ReviewSpec | None = None) -> ReviewData:
        current = spec or ReviewSpec()
        raw = self.repository.create(
            current.contract_name,
            current.duration_seconds,
            current.expected_risk_count,
        )
        return ReviewData(raw["id"], raw["status"], raw)

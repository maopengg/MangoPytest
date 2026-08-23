"""订单域 Service。"""

from auto_tests.api.pytest_api.services.common import ScenarioResult


class OrderService:
    def __init__(self, repository, factory):
        self.repository = repository
        self.factory = factory

    def create_valid_order(self) -> ScenarioResult:
        product = self._product(price=12.5)
        response = self.repository.create_order(
            self.factory.order(product["id"], 2), self.factory.unique("AUTO_ORDER")
        )
        return ScenarioResult({
            "created": response.status_code == 201,
            "amount_correct": float(self.repository.data(response)["total_amount"]) == 25.0,
        })

    def replay_same_idempotency_key(self) -> ScenarioResult:
        product = self._product(); key = self.factory.unique("AUTO_IDEMPOTENT")
        payload = self.factory.order(product["id"], 1)
        first = self.repository.create_order(payload, key)
        second = self.repository.create_order(payload, key)
        return ScenarioResult({
            "first_created": first.status_code == 201,
            "replayed": second.status_code == 200,
            "same_order": self.repository.data(first)["id"] == self.repository.data(second)["id"],
            "replay_flag": self.repository.data(second)["idempotency_replayed"] is True,
        })

    def reject_idempotency_conflict(self) -> ScenarioResult:
        product = self._product(); key = self.factory.unique("AUTO_IDEMPOTENT")
        first = self.repository.create_order(self.factory.order(product["id"], 1), key)
        second = self.repository.create_order(self.factory.order(product["id"], 2), key)
        return ScenarioResult({
            "first_created": first.status_code == 201,
            "conflict": second.status_code == 409,
            "business_code": second.json()["code"] == "IDEMPOTENCY_CONFLICT",
        })

    def reject_unknown_product(self) -> ScenarioResult:
        response = self.repository.create_order(
            self.factory.order(999999999, 1), self.factory.unique("AUTO_BAD_ORDER")
        )
        return ScenarioResult({"not_found": response.status_code == 404})

    def reject_zero_quantity(self) -> ScenarioResult:
        product = self._product()
        response = self.repository.create_order(
            self.factory.order(product["id"], 0), self.factory.unique("AUTO_BAD_ORDER")
        )
        return ScenarioResult({"validation_error": response.status_code == 422})

    def pay_pending_order(self) -> ScenarioResult:
        order = self._order()
        response = self.repository.request("POST", f"/api/v1/orders/{order['id']}/pay")
        return ScenarioResult({"success": response.status_code == 200, "paid": self.repository.data(response)["status"] == "paid"})

    def reject_duplicate_payment(self) -> ScenarioResult:
        order = self._order(); path = f"/api/v1/orders/{order['id']}/pay"
        first = self.repository.request("POST", path)
        second = self.repository.request("POST", path)
        return ScenarioResult({"first_paid": first.status_code == 200, "duplicate_rejected": second.status_code == 409})

    def refund_paid_order(self) -> ScenarioResult:
        order = self._order()
        paid = self.repository.request("POST", f"/api/v1/orders/{order['id']}/pay")
        refunded = self.repository.request("POST", f"/api/v1/orders/{order['id']}/refund")
        return ScenarioResult({
            "paid": paid.status_code == 200,
            "refunded": refunded.status_code == 200,
            "status_refunded": self.repository.data(refunded)["status"] == "refunded",
        })

    def reject_refund_before_payment(self) -> ScenarioResult:
        order = self._order()
        response = self.repository.request("POST", f"/api/v1/orders/{order['id']}/refund")
        return ScenarioResult({"conflict": response.status_code == 409})

    def _product(self, **overrides) -> dict:
        response = self.repository.create_product(self.factory.product(**overrides))
        return self.repository.data(response)

    def _order(self) -> dict:
        product = self._product()
        response = self.repository.create_order(
            self.factory.order(product["id"]), self.factory.unique("AUTO_ORDER")
        )
        return self.repository.data(response)

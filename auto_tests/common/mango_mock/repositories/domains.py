"""按业务域拆分的公共 Mango Mock 数据 Repository。"""

from typing import Any

from auto_tests.common.mango_mock import HttpResult

from .context import RepositoryContext


class TestRunRepository:
    def __init__(self, context: RepositoryContext):
        self.context = context

    def ensure(self) -> str:
        self.context.ensure_run()
        return self.context.run_id


class AuthRepository:
    def __init__(self, context: RepositoryContext):
        self.context = context

    def login(self, role: str) -> tuple[str, dict[str, Any]]:
        return self.context.login(role)


class OrderRepository:
    def __init__(self, context: RepositoryContext):
        self.context = context

    def products(self) -> list[dict[str, Any]]:
        return self.context.request_success(
            "GET", "/api/v1/products?page_size=100"
        )["items"]

    def create(self, product_id: int, quantity: int, key: str) -> dict[str, Any]:
        return self.context.request_success(
            "POST",
            "/api/v1/orders",
            json_data={"items": [{"product_id": product_id, "quantity": quantity}]},
            headers={"Idempotency-Key": key},
        )

    def pay(self, order_id: int) -> dict[str, Any]:
        return self.context.request_success("POST", f"/api/v1/orders/{order_id}/pay")

    def refund(self, order_id: int) -> dict[str, Any]:
        return self.context.request_success(
            "POST", f"/api/v1/orders/{order_id}/refund"
        )

    def get_result(self, order_id: int) -> HttpResult:
        result = self.context.request_result("GET", "/api/v1/orders")
        if result.status_code != 200:
            return result
        matched = next((item for item in result.data if item["id"] == order_id), None)
        if matched is None:
            return HttpResult(404, {"detail": f"订单不存在：{order_id}"}, result.headers)
        return HttpResult(200, {"data": matched}, result.headers)


class ClaimRepository:
    def __init__(self, context: RepositoryContext):
        self.context = context

    def create(self, amount: int, reason: str) -> dict[str, Any]:
        return self.context.request_success(
            "POST", "/api/v1/claims", json_data={"amount": amount, "reason": reason}
        )

    def get_result(self, claim_id: int) -> HttpResult:
        return self.context.request_result("GET", f"/api/v1/claims/{claim_id}")


class ReviewRepository:
    def __init__(self, context: RepositoryContext):
        self.context = context

    def create(
        self, contract_name: str, duration_seconds: int, expected_risk_count: int
    ) -> dict[str, Any]:
        return self.context.request_success(
            "POST",
            "/api/v1/reviews",
            json_data={
                "contract_name": contract_name,
                "duration_seconds": duration_seconds,
                "expected_risk_count": expected_risk_count,
            },
        )

    def get_result(self, review_id: int) -> HttpResult:
        return self.context.request_result("GET", f"/api/v1/reviews/{review_id}")

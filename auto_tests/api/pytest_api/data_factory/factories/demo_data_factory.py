"""L3：跨业务域 Demo 测试数据工厂。"""

from __future__ import annotations

import json
import uuid


class DemoDataFactory:
    @staticmethod
    def unique(prefix: str = "AUTO_PYTEST") -> str:
        return f"{prefix}_{uuid.uuid4().hex[:12]}"

    def product(self, **overrides) -> dict:
        payload = {
            "sku": self.unique("AUTO_SKU"),
            "name": self.unique("AUTO_PRODUCT"),
            "price": 12.5,
            "stock": 100,
        }
        payload.update(overrides)
        return payload

    @staticmethod
    def order(product_id: int, quantity: int = 1) -> dict:
        return {"items": [{"product_id": product_id, "quantity": quantity}]}

    def claim(self, amount: float = 12000, reason: str | None = None) -> dict:
        return {"amount": amount, "reason": reason or self.unique("AUTO_CLAIM")}

    def review(self, duration_seconds: int = 2) -> dict:
        return {
            "contract_name": self.unique("AUTO_CONTRACT"),
            "duration_seconds": duration_seconds,
            "expected_risk_count": 2,
        }

    def webhook_receiver(self, fail_first: int = 0) -> dict:
        key = self.unique("auto_receiver").lower()
        return {"receiver_key": key, "secret": self.unique("secret"), "fail_first": fail_first}

    @staticmethod
    def json_matrix() -> dict:
        return {
            "object": {"中文": "芒果", "nested": {"ok": True}},
            "array": [1, "two", False, None],
            "boolean": True,
            "null": None,
        }

    @staticmethod
    def webhook_body(delivery_id: str, payload: dict) -> bytes:
        return json.dumps(
            {"delivery_id": delivery_id, "event": "case.completed", "data": payload},
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode()

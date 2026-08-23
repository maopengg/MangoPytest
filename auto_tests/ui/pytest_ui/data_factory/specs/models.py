"""可组合的数据状态规格。"""

from dataclasses import dataclass


@dataclass(frozen=True)
class OrderSpec:
    status: str = "pending"
    quantity: int = 1

    def __post_init__(self) -> None:
        if self.status not in {"pending", "paid", "refunded"}:
            raise ValueError(f"不支持的订单状态：{self.status}")
        if self.quantity < 1:
            raise ValueError("订单数量必须大于 0")


@dataclass(frozen=True)
class ClaimSpec:
    amount: int = 12000
    reason: str = "AUTO_PYTEST_UI 前置报销"


@dataclass(frozen=True)
class ReviewSpec:
    contract_name: str = "AUTO_PYTEST_UI 合同"
    duration_seconds: int = 5
    expected_risk_count: int = 2


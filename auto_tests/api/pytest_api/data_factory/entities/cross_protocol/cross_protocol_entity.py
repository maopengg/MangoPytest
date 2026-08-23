"""跨协议场景的 L3 领域实体。"""

from pydantic import BaseModel, ConfigDict, Field


class CrossProtocolEntity(BaseModel):
    model_config = ConfigDict(extra="forbid")

    amount: float = Field(default=12000, gt=0, le=1_000_000)
    reason: str = Field(default="AUTO_PYTEST_跨协议报销", min_length=2, max_length=500)
    contract_name: str = Field(default="AUTO_PYTEST_跨协议合同", min_length=1, max_length=255)
    duration_seconds: int = Field(default=2, ge=1, le=30)
    expected_risk_count: int = Field(default=2, ge=0, le=100)

    def claim_payload(self) -> dict:
        return {"amount": self.amount, "reason": self.reason}

    def review_payload(self) -> dict:
        return {
            "contract_name": self.contract_name,
            "duration_seconds": self.duration_seconds,
            "expected_risk_count": self.expected_risk_count,
        }

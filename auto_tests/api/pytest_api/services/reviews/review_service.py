"""合同审查域 Service。"""

import time

from auto_tests.api.pytest_api.services.common import ScenarioResult


class ReviewService:
    def __init__(self, repository, factory):
        self.repository = repository
        self.factory = factory

    def start_review(self) -> ScenarioResult:
        response = self.repository.create_review(self.factory.review(2))
        return ScenarioResult({"accepted": response.status_code == 202, "has_id": bool(self.repository.data(response)["id"])})

    def poll_until_completed(self) -> ScenarioResult:
        review = self._review(1)
        data, progress = self._poll(review["id"])
        return ScenarioResult({"monotonic_progress": progress == sorted(progress), "completed": data["status"] == "completed"})

    def reject_empty_contract(self) -> ScenarioResult:
        response = self.repository.create_review({"contract_name": "", "duration_seconds": 1, "expected_risk_count": 1})
        return ScenarioResult({"validation_error": response.status_code == 422})

    def cancel_running_review(self) -> ScenarioResult:
        review = self._review(5)
        response = self.repository.request("DELETE", f"/api/v1/reviews/{review['id']}")
        return ScenarioResult({"success": response.status_code == 200, "cancelled": self.repository.data(response)["status"] == "cancelled"})

    def reject_cancel_completed_review(self) -> ScenarioResult:
        review = self._review(1)
        data, _ = self._poll(review["id"])
        cancelled = self.repository.request("DELETE", f"/api/v1/reviews/{review['id']}")
        return ScenarioResult({"completed": data["status"] == "completed", "cancel_rejected": cancelled.status_code == 409})

    def _review(self, duration: int) -> dict:
        return self.repository.data(self.repository.create_review(self.factory.review(duration)))

    def _poll(self, review_id: int) -> tuple[dict, list[int]]:
        progress = []
        for _ in range(12):
            response = self.repository.request("GET", f"/api/v1/reviews/{review_id}")
            data = self.repository.data(response); progress.append(data["progress"])
            if data["status"] == "completed":
                return data, progress
            time.sleep(0.15)
        return data, progress

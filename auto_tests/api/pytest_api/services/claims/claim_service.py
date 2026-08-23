"""报销审批域 Service。"""

from auto_tests.api.pytest_api.services.common import ScenarioResult


class ClaimService:
    def __init__(self, repository, factory):
        self.repository = repository
        self.factory = factory

    def submit_standard_claim(self) -> ScenarioResult:
        claim = self._claim(500)
        return ScenarioResult({"dept_pending": claim["status"] == "dept_pending", "has_task": len(claim["tasks"]) >= 1})

    def approve_large_claim(self) -> ScenarioResult:
        claim = self._claim(); states = self._approve_all(claim["id"])
        return ScenarioResult({"approval_sequence": states == ["finance_pending", "ceo_pending", "approved"]})

    def reject_out_of_turn_approval(self) -> ScenarioResult:
        claim = self._claim(); cid = claim["id"]
        response = self.repository.claim_action(cid, "finance_manager", "approve")
        current = self.repository.request("GET", f"/api/v1/claims/{cid}")
        return ScenarioResult({"rejected": response.status_code in {403, 409}, "state_unchanged": self.repository.data(current)["status"] == "dept_pending"})

    def reject_self_approval(self) -> ScenarioResult:
        response = self.repository.claim_action(self._claim()["id"], "employee", "approve")
        return ScenarioResult({"rejected": response.status_code in {403, 409}})

    def reject_claim(self) -> ScenarioResult:
        claim = self._claim(); cid = claim["id"]
        rejected = self.repository.claim_action(cid, "dept_manager", "reject")
        later = self.repository.claim_action(cid, "finance_manager", "approve")
        return ScenarioResult({"rejected": self.repository.data(rejected)["status"] == "rejected", "terminal": later.status_code in {403, 409}})

    def reject_repeated_task_action(self) -> ScenarioResult:
        cid = self._claim()["id"]
        first = self.repository.claim_action(cid, "dept_manager", "approve")
        second = self.repository.claim_action(cid, "dept_manager", "approve")
        return ScenarioResult({"first_success": first.status_code == 200, "repeat_rejected": second.status_code in {403, 409}})

    def withdraw_pending_claim(self) -> ScenarioResult:
        cid = self._claim()["id"]
        response = self.repository.request("POST", f"/api/v1/claims/{cid}/withdraw")
        return ScenarioResult({"success": response.status_code == 200, "withdrawn": self.repository.data(response)["status"] == "withdrawn"})

    def reject_withdraw_approved_claim(self) -> ScenarioResult:
        cid = self._claim()["id"]; self._approve_all(cid)
        response = self.repository.request("POST", f"/api/v1/claims/{cid}/withdraw")
        return ScenarioResult({"conflict": response.status_code == 409})

    def reject_foreign_withdrawal(self) -> ScenarioResult:
        cid = self._claim()["id"]
        response = self.repository.request("POST", f"/api/v1/claims/{cid}/withdraw", role="dept_manager")
        current = self.repository.request("GET", f"/api/v1/claims/{cid}")
        return ScenarioResult({"conflict": response.status_code == 409, "state_unchanged": self.repository.data(current)["status"] == "dept_pending"})

    def query_claim_and_tasks(self) -> ScenarioResult:
        cid = self._claim()["id"]
        self.repository.claim_action(cid, "dept_manager", "approve")
        response = self.repository.request("GET", f"/api/v1/claims/{cid}")
        data = self.repository.data(response)
        return ScenarioResult({"success": response.status_code == 200, "finance_pending": data["status"] == "finance_pending", "task_approved": data["tasks"][0]["status"] == "approved"})

    def enforce_cross_run_isolation(self) -> ScenarioResult:
        cid = self._claim()["id"]
        other = self.repository.create_test_run(self.factory.unique("AUTO_RUN"))
        run_id = self.repository.data(other)["id"]
        token = self.repository.data(self.repository.login(run_id))["access_token"]
        response = self.repository.request("GET", f"/api/v1/claims/{cid}", run_id=run_id, token=token)
        return ScenarioResult({"not_found": response.status_code == 404})

    def _claim(self, amount: float = 12000) -> dict:
        return self.repository.data(self.repository.create_claim(self.factory.claim(amount)))

    def _approve_all(self, claim_id: int) -> list[str]:
        return [
            self.repository.data(self.repository.claim_action(claim_id, role, "approve"))["status"]
            for role in ("dept_manager", "finance_manager", "ceo")
        ]

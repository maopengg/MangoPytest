"""故障注入与预置场景 Service。"""
import time
from auto_tests.api.pytest_api.services.common import ScenarioResult

class FaultService:
    SCENARIO = "EVENTUAL_SUCCESS_RETRY"
    def __init__(self, repository, factory): self.repository, self.factory = repository, factory

    def fixed_http_failure(self): return self._invoke_rule("always_fail", delay=0)
    def delayed_failure(self): return self._invoke_rule("delay_first", delay=0.3)
    def eventual_success(self): return self._run_scenario(backoff=False)
    def eventual_success_with_backoff(self): return self._run_scenario(backoff=True)

    def delete_fault_rule(self):
        key = self.factory.unique("auto_fault").lower()
        self.repository.request("POST", "/api/v1/faults", json={"rule_key": key, "mode": "always_fail", "failure_status": 500})
        before = self.repository.request("POST", f"/api/v1/faults/{key}/invoke")
        deleted = self.repository.request("DELETE", f"/api/v1/faults/{key}")
        after = self.repository.request("POST", f"/api/v1/faults/{key}/invoke")
        return ScenarioResult({"active_before": before.status_code == 500, "deleted": deleted.status_code == 200, "missing_after": after.status_code == 404})

    def reject_unknown_scenario(self):
        return ScenarioResult({"not_found": self.repository.request("POST", "/api/v1/scenarios/NOT_EXISTS/prepare").status_code == 404})

    def verify_incomplete_scenario(self):
        self.repository.request("POST", f"/api/v1/scenarios/{self.SCENARIO}/prepare")
        result = self.repository.data(self.repository.request("GET", f"/api/v1/scenarios/{self.SCENARIO}/verify"))
        return ScenarioResult({"not_passed": result["passed"] is False})

    def verify_completed_scenario(self):
        path = self._prepare(); [self.repository.request("POST", path) for _ in range(3)]
        result = self.repository.data(self.repository.request("GET", f"/api/v1/scenarios/{self.SCENARIO}/verify"))
        return ScenarioResult({"passed": result["passed"] is True})

    def _invoke_rule(self, mode, delay):
        key = self.factory.unique("auto_fault").lower()
        created = self.repository.request("POST", "/api/v1/faults", json={"rule_key": key, "mode": mode, "fail_count": 1, "failure_status": 500, "delay_seconds": delay})
        started = time.monotonic(); invoked = self.repository.request("POST", f"/api/v1/faults/{key}/invoke"); elapsed = time.monotonic() - started
        rules = self.repository.data(self.repository.request("GET", "/api/v1/faults")); rule = next(item for item in rules if item["rule_key"] == key)
        return ScenarioResult({"created": created.status_code == 200, "failed": invoked.status_code == 500, "delay_honored": elapsed >= delay - 0.02, "counted": rule["request_count"] == 1})

    def _run_scenario(self, backoff):
        path = self._prepare(); statuses = []
        for index in range(3):
            statuses.append(self.repository.request("POST", path).status_code)
            if backoff and index < 2: time.sleep(0.05 * (2 ** index))
        return ScenarioResult({"eventual_success": statuses == [500, 500, 200]})

    def _prepare(self):
        response = self.repository.request("POST", f"/api/v1/scenarios/{self.SCENARIO}/prepare")
        return self.repository.data(response)["prepared"]["invoke_path"]

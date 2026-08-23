"""Test Run 隔离域 Service。"""

import uuid

from auto_tests.api.pytest_api.services.common import ScenarioResult


class TestRunService:
    def __init__(self, repository, factory):
        self.repository = repository
        self.factory = factory

    def create_run(self) -> ScenarioResult:
        response = self.repository.create_test_run(self.factory.unique("AUTO_RUN"))
        return ScenarioResult(
            {"created": response.status_code == 201, "has_id": bool(self.repository.data(response)["id"])},
            {"response": response},
        )

    def verify_isolation(self) -> ScenarioResult:
        run_a = self._new_run(); run_b = self._new_run()
        token_a = self._token(run_a); token_b = self._token(run_b)
        payload = self.factory.product(sku=self.factory.unique("AUTO_SHARED"))
        created = self.repository.request(
            "POST", "/api/v1/products", run_id=run_a, token=token_a, json=payload
        )
        cross = self.repository.request(
            "GET", "/api/v1/products", run_id=run_b, token=token_b,
            params={"keyword": payload["sku"]},
        )
        return ScenarioResult(
            {"created_in_a": created.status_code == 201, "hidden_from_b": self.repository.data(cross)["total"] == 0}
        )

    def reject_unknown_run(self) -> ScenarioResult:
        response = self.repository.login(str(uuid.uuid4()))
        return ScenarioResult({"not_found": response.status_code == 404})

    def delete_populated_run(self) -> ScenarioResult:
        run_id = self._new_run(); token = self._token(run_id)
        created = self.repository.request(
            "POST", "/api/v1/products", run_id=run_id, token=token,
            json=self.factory.product(),
        )
        deleted = self.repository.delete_test_run(run_id)
        unavailable = self.repository.login(run_id)
        return ScenarioResult({
            "data_created": created.status_code == 201,
            "deleted": deleted.status_code == 200,
            "run_unavailable": unavailable.status_code == 404,
        })

    def cleanup_is_idempotent_for_active_run(self) -> ScenarioResult:
        run_id = self._new_run()
        first = self.repository.delete_test_run(run_id)
        second = self.repository.delete_test_run(run_id)
        active = self.repository.request("GET", "/api/v1/auth/me")
        return ScenarioResult({
            "first_deleted": first.status_code == 200,
            "second_not_found": second.status_code == 404,
            "fixture_run_alive": active.status_code == 200,
        })

    def _new_run(self) -> str:
        response = self.repository.create_test_run(self.factory.unique("AUTO_RUN"))
        return self.repository.data(response)["id"]

    def _token(self, run_id: str) -> str:
        return self.repository.data(self.repository.login(run_id))["access_token"]

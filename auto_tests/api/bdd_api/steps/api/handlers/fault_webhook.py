"""故障、场景目录与 Webhook 功能场景。"""

from __future__ import annotations

import time

from .base import BaseHandler


class FaultWebhookHandler(BaseHandler):
    def _fault_webhook(self, case_id: str, n: int) -> FunctionalCaseResult:
        if n <= 87:
            return self._fault(case_id, n)
        return self._webhook(case_id, n)

    def _fault(self, case_id: str, n: int) -> FunctionalCaseResult:
        r = self.repo
        if n in {80, 81}:
            key = self.factory.unique("auto_fault").lower(); payload = {"rule_key": key, "mode": "always_fail" if n == 80 else "delay_first", "fail_count": 1, "failure_status": 500, "delay_seconds": 0 if n == 80 else 0.3}
            created = r.request("POST", "/api/v1/faults", json=payload); started = time.monotonic(); invoked = r.request("POST", f"/api/v1/faults/{key}/invoke"); elapsed = time.monotonic() - started
            listed = r.data(r.request("GET", "/api/v1/faults"))
            rule = next(item for item in listed if item["rule_key"] == key)
            return self.result(case_id, created.status_code == 200, invoked.status_code == 500, (elapsed >= 0.28 if n == 81 else True), rule["request_count"] == 1)
        if n in {82, 83}:
            prepared = r.request("POST", "/api/v1/scenarios/EVENTUAL_SUCCESS_RETRY/prepare"); path = r.data(prepared)["prepared"]["invoke_path"]
            statuses = []
            for index in range(3):
                statuses.append(r.request("POST", path).status_code)
                if n == 83 and index < 2: time.sleep(0.05 * (2 ** index))
            return self.result(case_id, statuses == [500, 500, 200])
        if n == 84:
            key = self.factory.unique("auto_fault").lower(); r.request("POST", "/api/v1/faults", json={"rule_key": key, "mode": "always_fail", "failure_status": 500})
            before = r.request("POST", f"/api/v1/faults/{key}/invoke"); deleted = r.request("DELETE", f"/api/v1/faults/{key}"); after = r.request("POST", f"/api/v1/faults/{key}/invoke")
            return self.result(case_id, before.status_code == 500, deleted.status_code == 200, after.status_code == 404)
        if n == 85:
            return self.result(case_id, r.request("POST", "/api/v1/scenarios/NOT_EXISTS/prepare").status_code == 404)
        if n == 86:
            r.request("POST", "/api/v1/scenarios/EVENTUAL_SUCCESS_RETRY/prepare")
            verify = r.request("GET", "/api/v1/scenarios/EVENTUAL_SUCCESS_RETRY/verify")
            return self.result(case_id, r.data(verify)["passed"] is False)
        prepared = r.request("POST", "/api/v1/scenarios/EVENTUAL_SUCCESS_RETRY/prepare"); path = r.data(prepared)["prepared"]["invoke_path"]
        [r.request("POST", path) for _ in range(3)]
        verify = r.request("GET", "/api/v1/scenarios/EVENTUAL_SUCCESS_RETRY/verify")
        return self.result(case_id, r.data(verify)["passed"] is True)

    def _receiver(self, fail_first: int = 0):
        payload = self.factory.webhook_receiver(fail_first)
        response = self.repo.request("POST", "/api/v1/webhooks/receivers", json=payload)
        return self.repo.data(response)

    def _webhook(self, case_id: str, n: int) -> FunctionalCaseResult:
        r = self.repo
        receiver = self._receiver(1 if n == 89 else (10 if n == 90 else 0))
        if n in {88, 89, 90, 94}:
            payload = self.factory.json_matrix() if n == 94 else {"case_id": n}
            dispatch = r.request("POST", "/api/v1/webhooks/dispatch", params={"wait": "true"}, json={"callback_url": receiver["callback_url"], "event_type": "case.completed", "payload": payload, "secret": receiver["secret"], "max_attempts": 3, "retry_interval_ms": 0})
            delivery = r.data(dispatch)
            delivery = r.data(r.request("GET", f"/api/v1/webhooks/deliveries/{delivery['id']}"))
            receipts = r.data(r.request("GET", f"/api/v1/webhooks/receivers/{receiver['receiver_key']}/receipts"))
            if n == 88: return self.result(case_id, delivery["status"] == "succeeded", len(receipts) == 1, receipts[0]["signature_valid"] is True)
            if n == 89: return self.result(case_id, delivery["status"] == "succeeded", delivery["attempts"] == 2, len(receipts) == 2)
            if n == 90: return self.result(case_id, delivery["status"] == "failed", delivery["attempts"] == 3, len(receipts) == 3)
            return self.result(case_id, receipts[-1]["payload"]["data"] == payload)
        delivery_id = self.factory.unique("delivery")
        body = self.factory.webhook_body(delivery_id, {"ok": True})
        headers = r.webhook_headers(receiver["secret"], delivery_id, body, int(time.time()) - 7200 if n == 92 else None)
        if n == 91: headers["X-Mango-Signature"] = "sha256=invalid"
        first = r.post_callback(receiver["callback_url"], headers=headers, content=body)
        if n in {91, 92}:
            return self.result(case_id, first.status_code == 401)
        if n == 93:
            second = r.post_callback(receiver["callback_url"], headers=headers, content=body)
            receipts = r.data(r.request("GET", f"/api/v1/webhooks/receivers/{receiver['receiver_key']}/receipts"))
            return self.result(case_id, first.status_code == 200, second.status_code == 200, len(receipts) == 2, len({item["delivery_id"] for item in receipts}) == 1)
        other, _ = self._new_run(); token = self._login(other).json()["data"]["access_token"]
        dispatched = r.request("POST", "/api/v1/webhooks/dispatch", params={"wait": "true"}, json={"callback_url": receiver["callback_url"], "event_type": "case.completed", "payload": {}, "secret": receiver["secret"], "max_attempts": 1, "retry_interval_ms": 0})
        foreign = r.request("GET", f"/api/v1/webhooks/deliveries/{r.data(dispatched)['id']}", run_id=other, token=token)
        return self.result(case_id, foreign.status_code == 404)

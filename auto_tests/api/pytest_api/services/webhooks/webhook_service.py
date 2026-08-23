"""Webhook 投递域 Service。"""
import time
from auto_tests.api.pytest_api.services.common import ScenarioResult

class WebhookService:
    def __init__(self, repository, factory): self.repository, self.factory = repository, factory

    def deliver_signed_webhook(self): return self._dispatch(fail_first=0, expected_status="succeeded", attempts=1)
    def retry_once_then_succeed(self): return self._dispatch(fail_first=1, expected_status="succeeded", attempts=2)
    def exhaust_retries(self): return self._dispatch(fail_first=10, expected_status="failed", attempts=3)
    def preserve_complex_payload(self): return self._dispatch(fail_first=0, expected_status="succeeded", attempts=1, payload=self.factory.json_matrix())
    def reject_tampered_signature(self): return self._direct(signature_invalid=True)
    def reject_expired_signature(self): return self._direct(expired=True)

    def accept_duplicate_delivery_id(self):
        receiver = self._receiver(); delivery_id = self.factory.unique("delivery")
        body = self.factory.webhook_body(delivery_id, {"ok": True})
        headers = self.repository.webhook_headers(receiver["secret"], delivery_id, body)
        first = self.repository.post_callback(receiver["callback_url"], headers=headers, content=body)
        second = self.repository.post_callback(receiver["callback_url"], headers=headers, content=body)
        receipts = self._receipts(receiver)
        return ScenarioResult({"first_ok": first.status_code == 200, "second_ok": second.status_code == 200, "two_receipts": len(receipts) == 2, "same_delivery": len({item["delivery_id"] for item in receipts}) == 1})

    def enforce_cross_run_isolation(self):
        receiver = self._receiver(); delivery = self._dispatch_request(receiver, {})
        other = self.repository.create_test_run(self.factory.unique("AUTO_RUN")); run_id = self.repository.data(other)["id"]
        token = self.repository.data(self.repository.login(run_id))["access_token"]
        response = self.repository.request("GET", f"/api/v1/webhooks/deliveries/{delivery['id']}", run_id=run_id, token=token)
        return ScenarioResult({"not_found": response.status_code == 404})

    def _dispatch(self, fail_first, expected_status, attempts, payload=None):
        receiver = self._receiver(fail_first); payload = payload or {"case": "AUTO"}
        delivery = self._dispatch_request(receiver, payload)
        current = self.repository.data(self.repository.request("GET", f"/api/v1/webhooks/deliveries/{delivery['id']}"))
        receipts = self._receipts(receiver)
        checks = {"status": current["status"] == expected_status, "attempts": current["attempts"] == attempts, "receipt_count": len(receipts) == attempts}
        if expected_status == "succeeded": checks["signature_valid"] = receipts[-1]["signature_valid"] is True
        if payload: checks["payload_preserved"] = receipts[-1]["payload"]["data"] == payload
        return ScenarioResult(checks)

    def _direct(self, signature_invalid=False, expired=False):
        receiver = self._receiver(); delivery_id = self.factory.unique("delivery")
        body = self.factory.webhook_body(delivery_id, {"ok": True})
        headers = self.repository.webhook_headers(receiver["secret"], delivery_id, body, int(time.time()) - 7200 if expired else None)
        if signature_invalid: headers["X-Mango-Signature"] = "sha256=invalid"
        response = self.repository.post_callback(receiver["callback_url"], headers=headers, content=body)
        return ScenarioResult({"unauthorized": response.status_code == 401})

    def _receiver(self, fail_first=0):
        response = self.repository.request("POST", "/api/v1/webhooks/receivers", json=self.factory.webhook_receiver(fail_first))
        return self.repository.data(response)

    def _dispatch_request(self, receiver, payload):
        response = self.repository.request("POST", "/api/v1/webhooks/dispatch", params={"wait": "true"}, json={"callback_url": receiver["callback_url"], "event_type": "case.completed", "payload": payload, "secret": receiver["secret"], "max_attempts": 3, "retry_interval_ms": 0})
        return self.repository.data(response)

    def _receipts(self, receiver):
        response = self.repository.request("GET", f"/api/v1/webhooks/receivers/{receiver['receiver_key']}/receipts")
        return self.repository.data(response)

"""SSE 协议 Service。"""
from auto_tests.api.pytest_api.services.common import ScenarioResult

class SseService:
    def __init__(self, repository, factory): self.repository, self.factory = repository, factory

    def finite_standard_stream(self):
        text = self._lab(count=3).text
        return ScenarioResult({"three_ids": text.count("id:") == 3, "completed": "event: lab.completed" in text})

    def standard_event_fields(self):
        text = self._lab(count=3).text
        return ScenarioResult({"id": "id: 1" in text, "event": "event: lab.item" in text, "data": "data:" in text})

    def heartbeat_stream(self):
        events = self.repository.sse_events(topic="unused", max_events=2, max_duration_seconds=2)
        return ScenarioResult({"heartbeat": any(item.get("event") == "heartbeat" for item in events)})

    def reconnect_with_last_event_id(self): return self._resume_claim_events()

    def server_closes_after_event(self):
        text = self._lab(count=3, close_after=2).text
        return ScenarioResult({"second_received": "id: 2" in text, "not_completed": "lab.completed" not in text})

    def resume_remaining_events(self): return self._resume_claim_events()

    def multiline_data(self):
        text = self.repository.request("GET", "/api/v1/events/lab/raw", params={"mode": "multiline", "interval_ms": 0}).text
        return ScenarioResult({"first_line": 'data: {"run_id"' in text, "second_line": 'data: "line":"second"}' in text})

    def comments_bom_and_partial_chunks(self):
        outputs = {mode: self.repository.request("GET", "/api/v1/events/lab/raw", params={"mode": mode, "interval_ms": 0}).content for mode in ("comments", "bom", "partial")}
        return ScenarioResult({"comment": b": heartbeat comment" in outputs["comments"], "bom": outputs["bom"].startswith(b"\xef\xbb\xbf"), "partial": b"started" in outputs["partial"]})

    def malformed_event_recovery(self):
        text = self._lab(count=3, malformed_at=2).text
        return ScenarioResult({"malformed_present": '{"invalid":' in text, "continues": "id: 3" in text})

    def stop_with_no_content(self):
        response = self.repository.request("GET", "/api/v1/events/lab/raw", params={"mode": "stop"})
        return ScenarioResult({"no_content": response.status_code == 204, "empty": response.content == b""})

    def _lab(self, **params):
        params.setdefault("interval_ms", 0)
        return self.repository.request("GET", "/api/v1/events/lab", params=params)

    def _resume_claim_events(self):
        claim = self.repository.data(self.repository.create_claim(self.factory.claim()))
        first = self.repository.sse_events(topic="approval", aggregate_id=claim["id"], max_events=1, max_duration_seconds=2)[0]
        self.repository.claim_action(claim["id"], "dept_manager", "approve")
        resumed = self.repository.sse_events(topic="approval", aggregate_id=claim["id"], last_event_id=first["id"], max_events=2, max_duration_seconds=2)
        ids = [int(item["id"]) for item in resumed if item.get("id")]
        return ScenarioResult({"has_events": bool(ids), "after_cursor": all(value > int(first["id"]) for value in ids), "no_duplicates": len(ids) == len(set(ids))})

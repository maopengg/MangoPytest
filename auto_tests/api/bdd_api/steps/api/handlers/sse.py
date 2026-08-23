"""SSE 功能场景。"""

from __future__ import annotations

from .base import BaseHandler


class SseHandler(BaseHandler):
    def _sse(self, case_id: str, n: int) -> FunctionalCaseResult:
        r = self.repo
        if n in {96, 97, 100, 104}:
            params = {"count": 3, "interval_ms": 0}
            if n == 100: params["close_after"] = 2
            if n == 104: params["malformed_at"] = 2
            response = r.request("GET", "/api/v1/events/lab", params=params)
            text = response.text
            if n == 96: return self.result(case_id, text.count("id:") == 3, "event: lab.completed" in text)
            if n == 97: return self.result(case_id, all(value in text for value in ("id: 1", "event: lab.item", "data:")))
            if n == 100: return self.result(case_id, "id: 2" in text, "lab.completed" not in text)
            return self.result(case_id, '{"invalid":' in text, "id: 3" in text)
        if n == 98:
            events = r.sse_events(topic="unused", max_events=2, max_duration_seconds=2)
            return self.result(case_id, any(item.get("event") == "heartbeat" for item in events))
        if n in {99, 101}:
            claim = self._claim(); first = r.sse_events(topic="approval", aggregate_id=claim["id"], max_events=1, max_duration_seconds=2)[0]
            r.claim_action(claim["id"], "dept_manager", "approve")
            resumed = r.sse_events(topic="approval", aggregate_id=claim["id"], last_event_id=first["id"], max_events=2, max_duration_seconds=2)
            ids = [int(item["id"]) for item in resumed if item.get("id")]
            return self.result(case_id, bool(ids), all(value > int(first["id"]) for value in ids), len(ids) == len(set(ids)))
        if n == 102:
            text = r.request("GET", "/api/v1/events/lab/raw", params={"mode": "multiline", "interval_ms": 0}).text
            return self.result(case_id, 'data: {"run_id"' in text, 'data: "line":"second"}' in text)
        if n == 103:
            outputs = {mode: r.request("GET", "/api/v1/events/lab/raw", params={"mode": mode, "interval_ms": 0}).content for mode in ("comments", "bom", "partial")}
            return self.result(case_id, b": heartbeat comment" in outputs["comments"], outputs["bom"].startswith(b"\xef\xbb\xbf"), b"started" in outputs["partial"])
        response = r.request("GET", "/api/v1/events/lab/raw", params={"mode": "stop"})
        return self.result(case_id, response.status_code == 204, response.content == b"")

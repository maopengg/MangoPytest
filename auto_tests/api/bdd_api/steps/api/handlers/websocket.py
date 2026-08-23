"""WebSocket 功能场景。"""

from __future__ import annotations

import json

from websockets.exceptions import ConnectionClosed

from .base import BaseHandler


class WebSocketHandler(BaseHandler):
    def _websocket(self, case_id: str, n: int) -> FunctionalCaseResult:
        r = self.repo
        if n in {107, 108}:
            return self.result(case_id, r.websocket_rejected(missing_run=n == 107))
        with r.websocket_session() as socket:
            connected = json.loads(r.websocket_receive(socket))
            if n == 106: return self.result(case_id, connected["type"] == "connected", connected["data"]["test_run_id"] == r.run_id)
            if n == 109:
                value = r.websocket_send(socket, {"action": "ping", "data": "AUTO"}); return self.result(case_id, value == {"type": "pong", "data": "AUTO"})
            if n == 110:
                data = self.factory.json_matrix(); value = r.websocket_send(socket, {"action": "echo", "data": data}); return self.result(case_id, value["data"] == data)
            if n == 111:
                r.websocket_send_raw(socket, b"\x00\xffbinary"); return self.result(case_id, r.websocket_receive(socket) == b"\x00\xffbinary")
            if n == 112:
                r.websocket_send_raw(socket, "not-json"); value = json.loads(r.websocket_receive(socket)); return self.result(case_id, value["error"]["code"] == "INVALID_JSON")
            if n == 113:
                value = r.websocket_send(socket, {"action": "not_exists"}); return self.result(case_id, value["error"]["code"] == "UNKNOWN_ACTION")
            if n in {114, 117, 119}:
                claim = self._claim(); cid = claim["id"]
                if n == 119: r.websocket_send(socket, {"action": "slow_consumer", "delay_ms": 20})
                subscribed = r.websocket_send(socket, {"action": "subscribe", "topic": "approval", "aggregate_id": cid, "after_id": 0})
                event = r.websocket_receive_type(socket, "business.event")
                if n == 117:
                    first_id = event["data"]["id"]
                    r.claim_action(cid, "dept_manager", "approve")
                    return self.result(case_id, subscribed["type"] == "subscribed", int(r.websocket_receive_type(socket, "business.event")["data"]["id"]) > int(first_id))
                return self.result(case_id, subscribed["type"] == "subscribed", event["data"]["aggregate_id"] == str(cid))
            if n == 115:
                value = r.websocket_send(socket, {"action": "subscribe"}); return self.result(case_id, value["error"]["code"] == "TOPIC_REQUIRED")
            if n == 116:
                r.websocket_send(socket, {"action": "subscribe", "topic": "review"}); value = r.websocket_send(socket, {"action": "unsubscribe", "topic": "review"})
                return self.result(case_id, value["type"] == "unsubscribed", value["data"]["existed"] is True)
            if n == 118:
                r.websocket_send_raw(socket, json.dumps({"action": "burst", "count": 1000})); indexes = [json.loads(r.websocket_receive(socket))["data"]["index"] for _ in range(1000)]
                return self.result(case_id, indexes == list(range(1, 1001)))
            if n == 120:
                claim = self._claim(); value = r.websocket_send(socket, {"action": "approve", "claim_id": claim["id"], "decision": "approve"})
                return self.result(case_id, value["type"] == "approval.result", value["data"]["status"] == "finance_pending")
            r.websocket_send_raw(socket, json.dumps({"action": "close", "code": 1000, "reason": "AUTO_CLOSE"}))
            try: r.websocket_receive(socket)
            except ConnectionClosed as error:
                return self.result(
                    case_id,
                    error.rcvd is not None and error.rcvd.code == 1000,
                    error.rcvd is not None and error.rcvd.reason == "AUTO_CLOSE",
                )
        return self.result(case_id, False)

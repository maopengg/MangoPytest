"""WebSocket 协议 Service。"""
import json
from websockets.exceptions import ConnectionClosed
from auto_tests.api.pytest_api.services.common import ScenarioResult

class WebSocketService:
    def __init__(self, repository, factory): self.repository, self.factory = repository, factory

    def connect_with_credentials(self):
        with self.repository.websocket_session() as socket:
            connected = json.loads(socket.recv(timeout=5))
        return ScenarioResult({"connected": connected["type"] == "connected", "run_id": connected["data"]["test_run_id"] == self.repository.run_id})

    def reject_missing_run(self):
        return ScenarioResult({"rejected": self.repository.websocket_rejected(f"{self.repository.websocket_url}?token=invalid")})

    def reject_invalid_token(self):
        url = f"{self.repository.websocket_url}?test_run_id={self.repository.run_id}&token=invalid"
        return ScenarioResult({"rejected": self.repository.websocket_rejected(url)})

    def ping_pong(self): return self._exchange({"action": "ping", "data": "AUTO"}, lambda value: value == {"type": "pong", "data": "AUTO"}, "pong")

    def echo_json(self):
        payload = self.factory.json_matrix()
        return self._exchange({"action": "echo", "data": payload}, lambda value: value["data"] == payload, "json_echo")

    def echo_binary(self):
        with self.repository.websocket_session() as socket:
            socket.recv(timeout=5); socket.send(b"\x00\xffbinary"); response = socket.recv(timeout=5)
        return ScenarioResult({"binary_echo": response == b"\x00\xffbinary"})

    def reject_invalid_json(self):
        with self.repository.websocket_session() as socket:
            socket.recv(timeout=5); socket.send("not-json"); value = json.loads(socket.recv(timeout=5))
        return ScenarioResult({"invalid_json": value["error"]["code"] == "INVALID_JSON"})

    def reject_unknown_action(self): return self._exchange({"action": "not_exists"}, lambda value: value["error"]["code"] == "UNKNOWN_ACTION", "unknown_action")
    def subscribe_business_event(self): return self._subscription(False, False)
    def reject_missing_topic(self): return self._exchange({"action": "subscribe"}, lambda value: value["error"]["code"] == "TOPIC_REQUIRED", "topic_required")

    def unsubscribe_topic(self):
        with self.repository.websocket_session() as socket:
            socket.recv(timeout=5); self.repository.websocket_send(socket, {"action": "subscribe", "topic": "review"})
            value = self.repository.websocket_send(socket, {"action": "unsubscribe", "topic": "review"})
        return ScenarioResult({"unsubscribed": value["type"] == "unsubscribed", "existed": value["data"]["existed"] is True})

    def resume_subscription(self): return self._subscription(True, False)

    def receive_burst(self):
        with self.repository.websocket_session() as socket:
            socket.recv(timeout=5); socket.send(json.dumps({"action": "burst", "count": 1000}))
            indexes = [json.loads(socket.recv(timeout=5))["data"]["index"] for _ in range(1000)]
        return ScenarioResult({"ordered": indexes == list(range(1, 1001))})

    def tolerate_slow_consumer(self): return self._subscription(False, True)

    def server_close(self):
        code = reason = None
        with self.repository.websocket_session() as socket:
            socket.recv(timeout=5); socket.send(json.dumps({"action": "close", "code": 1000, "reason": "AUTO_CLOSE"}))
            try: socket.recv(timeout=5)
            except ConnectionClosed as error:
                if error.rcvd: code, reason = error.rcvd.code, error.rcvd.reason
        return ScenarioResult({"normal_code": code == 1000, "reason": reason == "AUTO_CLOSE"})

    def _exchange(self, payload, predicate, name):
        with self.repository.websocket_session() as socket:
            socket.recv(timeout=5); value = self.repository.websocket_send(socket, payload)
        return ScenarioResult({name: predicate(value)})

    def _subscription(self, resume, slow):
        claim = self.repository.data(self.repository.create_claim(self.factory.claim())); cid = claim["id"]
        with self.repository.websocket_session() as socket:
            socket.recv(timeout=5)
            if slow: self.repository.websocket_send(socket, {"action": "slow_consumer", "delay_ms": 20})
            subscribed = self.repository.websocket_send(socket, {"action": "subscribe", "topic": "approval", "aggregate_id": cid, "after_id": 0})
            event = self.repository.websocket_receive_type(socket, "business.event")
            checks = {"subscribed": subscribed["type"] == "subscribed", "aggregate": event["data"]["aggregate_id"] == str(cid)}
            if resume:
                first_id = event["data"]["id"]; self.repository.claim_action(cid, "dept_manager", "approve")
                second = self.repository.websocket_receive_type(socket, "business.event")
                checks["cursor_advanced"] = int(second["data"]["id"]) > int(first_id)
        return ScenarioResult(checks)

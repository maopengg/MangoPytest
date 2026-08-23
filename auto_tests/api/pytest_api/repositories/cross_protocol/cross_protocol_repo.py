"""跨协议业务域 L2 Repository，负责协议访问和 Test Run 清理。"""

from __future__ import annotations

import json
import os
import uuid
from urllib.parse import urlparse

from auto_tests.common.mango_mock import (
    GrpcProtocolClient,
    HttpProtocolClient,
    McpProtocolClient,
    SseProtocolClient,
    WebSocketProtocolClient,
)
from core.utils import log


class CrossProtocolRepository:
    PASSWORDS = {
        "employee": "password123",
        "dept_manager": "password123",
        "finance_manager": "password123",
        "ceo": "password123",
    }

    def __init__(self, base_url: str, timeout: int = 30, admin_token: str | None = None):
        self.base_url = base_url.rstrip("/")
        self.http = HttpProtocolClient(self.base_url, timeout=timeout)
        self.websocket = WebSocketProtocolClient(self.base_url)
        self.sse = SseProtocolClient(self.base_url, timeout=timeout)
        self.mcp = McpProtocolClient(self.base_url, timeout=timeout)
        host = urlparse(self.base_url).hostname or "127.0.0.1"
        self.grpc = GrpcProtocolClient(f"{host}:50051")
        self.run_id = ""
        self.tokens: dict[str, str] = {}
        self.admin_token = admin_token

    def start(self) -> "CrossProtocolRepository":
        name = f"AUTO_PYTEST_{uuid.uuid4().hex[:10]}"
        response = self.http.create_run(name, ttl_minutes=5)
        assert response.status_code == 201, response.body
        assert response.body.get("code") == 0, response.body
        self.run_id = response.data["id"]
        log.info(f"创建隔离 Test Run: {self.run_id}")
        return self

    def token(self, role: str) -> str:
        if role not in self.tokens:
            response = self.http.login(self.run_id, role, self.PASSWORDS[role])
            assert response.status_code == 200, response.body
            self.tokens[role] = response.data["access_token"]
        return self.tokens[role]

    def close(self) -> None:
        admin_token = self.admin_token or os.getenv("MANGO_MOCK_ADMIN_TOKEN")
        if self.run_id and admin_token:
            response = self.http.delete_run(self.run_id, admin_token)
            if response.status_code != 200:
                log.warning(f"Test Run 立即清理失败，将由 TTL 回收: {self.run_id}")
        elif self.run_id:
            log.debug(f"未配置管理员令牌，Test Run 将由 TTL 回收: {self.run_id}")
        self.mcp.close()
        self.grpc.close()
        self.http.close()

    def create_claim_http(self, payload: dict) -> dict:
        result = self.http.request(
            "POST", "/api/v1/claims", run_id=self.run_id,
            token=self.token("employee"), json_data=payload,
        )
        assert result.status_code == 201, result.body
        return result.data

    def get_claim_http(self, claim_id: int, role: str = "employee"):
        return self.http.request(
            "GET", f"/api/v1/claims/{claim_id}", run_id=self.run_id,
            token=self.token(role),
        )

    def act_claim_http(self, claim_id: int, role: str, decision: str = "approve") -> dict:
        result = self.http.request(
            "POST", f"/api/v1/claims/{claim_id}/actions", run_id=self.run_id,
            token=self.token(role), json_data={"action": decision, "comment": "AUTO_PYTEST"},
        )
        assert result.status_code == 200, result.body
        return result.data

    def approve_websocket(self, claim_id: int, role: str) -> dict:
        with self.websocket.session(self.run_id, self.token(role)) as socket:
            connected = json.loads(socket.recv(timeout=10))
            assert connected["type"] == "connected"
            result = self.websocket.send(
                socket,
                {"action": "approve", "claim_id": claim_id, "decision": "approve", "comment": "AUTO_PYTEST"},
            )
            assert result["type"] == "approval.result", result
            return result["data"]

    def websocket_event(
        self, *, topic: str, role: str = "employee", aggregate_id: int | None = None,
        after_id: int = 0,
    ) -> dict:
        with self.websocket.session(self.run_id, self.token(role)) as socket:
            connected = json.loads(socket.recv(timeout=10))
            assert connected["type"] == "connected"
            subscribed = self.websocket.send(
                socket,
                {"action": "subscribe", "topic": topic, "aggregate_id": aggregate_id, "after_id": after_id},
            )
            assert subscribed["type"] == "subscribed", subscribed
            return self.websocket.receive_type(socket, "business.event")["data"]

    def create_claim_mcp(self, payload: dict) -> dict:
        result = self.mcp.call_tool(
            self.run_id, self.token("employee"), "create_expense_claim", payload
        )
        assert not result.get("isError"), result
        return result["value"]

    def act_claim_mcp(self, claim_id: int, role: str, decision: str = "approve") -> dict:
        result = self.mcp.call_tool(
            self.run_id, self.token(role), "approve_expense_claim",
            {"claim_id": claim_id, "decision": decision, "comment": "AUTO_PYTEST"},
        )
        assert not result.get("isError"), result
        return result["value"]

    def get_claim_mcp(self, claim_id: int, role: str = "employee") -> dict:
        return self.mcp.call_tool(
            self.run_id, self.token(role), "get_expense_workflow", {"claim_id": claim_id}
        )

    def create_claim_grpc(self, payload: dict):
        return self.grpc.create_claim(
            self.run_id, self.token("employee"), payload["amount"], payload["reason"]
        )

    def act_claim_grpc(self, claim_id: int, role: str, decision: str = "approve"):
        return self.grpc.act_claim(self.run_id, self.token(role), claim_id, decision)

    def get_claim_grpc(self, claim_id: int, role: str = "employee"):
        return self.grpc.get_claim(self.run_id, self.token(role), claim_id)

    def start_review_http(self, payload: dict) -> dict:
        result = self.http.request(
            "POST", "/api/v1/reviews", run_id=self.run_id,
            token=self.token("employee"), json_data=payload,
        )
        assert result.status_code == 202, result.body
        return result.data

    def get_review_http(self, job_id: int):
        return self.http.request(
            "GET", f"/api/v1/reviews/{job_id}", run_id=self.run_id,
            token=self.token("employee"),
        )

    def start_review_grpc(self, payload: dict):
        return self.grpc.start_review(
            self.run_id, self.token("employee"), payload["contract_name"],
            payload["duration_seconds"], payload["expected_risk_count"],
        )

    def cancel_review_mcp(self, job_id: int) -> dict:
        result = self.mcp.call_tool(
            self.run_id, self.token("employee"), "cancel_contract_review", {"job_id": job_id}
        )
        assert not result.get("isError"), result
        return result["value"]

    def sse_events(self, **kwargs):
        return self.sse.events(self.run_id, self.token("employee"), **kwargs)

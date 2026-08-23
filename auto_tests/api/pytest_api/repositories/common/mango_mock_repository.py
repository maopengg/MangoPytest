"""L2：Mango Mock 公共协议 Gateway。"""

from __future__ import annotations

import hashlib
import hmac
import time
from typing import Any

import httpx
from websockets.sync.client import connect

from auto_tests.api.pytest_api.repositories.cross_protocol import CrossProtocolRepository


class MangoMockRepository:
    def __init__(self, runtime: CrossProtocolRepository):
        self.runtime = runtime
        self.base_url = runtime.base_url
        self.client = runtime.http

    @property
    def run_id(self) -> str:
        return self.runtime.run_id

    def close(self) -> None:
        # HTTP 客户端归 CrossProtocolRepository 所有，由运行时统一关闭。
        pass

    def headers(
        self,
        role: str | None = "employee",
        *,
        run_id: str | None = None,
        token: str | None = None,
    ) -> dict[str, str]:
        result = {"X-Test-Run-ID": run_id or self.run_id, "X-Tenant-ID": "tenant-a"}
        if token is not None:
            result["Authorization"] = f"Bearer {token}"
        elif role is not None:
            result["Authorization"] = f"Bearer {self.runtime.token(role)}"
        return result

    def request(
        self,
        method: str,
        path: str,
        *,
        role: str | None = "employee",
        run_id: str | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        follow_redirects: bool = False,
        timeout: float | None = None,
        **kwargs: Any,
    ) -> httpx.Response:
        merged = {**self.headers(role, run_id=run_id, token=token), **(headers or {})}
        return self.client.request_raw(
            method,
            path,
            headers=merged,
            follow_redirects=follow_redirects,
            timeout=timeout,
            **kwargs,
        )

    @staticmethod
    def data(response: httpx.Response) -> Any:
        return response.json().get("data")

    def create_product(self, payload: dict) -> httpx.Response:
        return self.request("POST", "/api/v1/products", json=payload)

    def list_products(self, **params) -> httpx.Response:
        return self.request("GET", "/api/v1/products", params=params)

    def create_order(self, payload: dict, key: str) -> httpx.Response:
        return self.request(
            "POST", "/api/v1/orders", json=payload,
            headers={"Idempotency-Key": key},
        )

    def create_claim(self, payload: dict, role: str = "employee") -> httpx.Response:
        return self.request("POST", "/api/v1/claims", role=role, json=payload)

    def claim_action(self, claim_id: int, role: str, action: str) -> httpx.Response:
        return self.request(
            "POST", f"/api/v1/claims/{claim_id}/actions", role=role,
            json={"action": action, "comment": "AUTO_PYTEST"},
        )

    def create_review(self, payload: dict) -> httpx.Response:
        return self.request("POST", "/api/v1/reviews", json=payload)

    def create_test_run(self, name: str, ttl_minutes: int = 5) -> httpx.Response:
        return self.client.request_raw(
            "POST", "/api/v1/test-runs",
            json={"name": name, "tenant_id": "tenant-a", "ttl_minutes": ttl_minutes},
        )

    def login(
        self, run_id: str, username: str = "employee", password: str = "password123"
    ) -> httpx.Response:
        return self.client.request_raw(
            "POST", "/api/v1/auth/login", headers={"X-Test-Run-ID": run_id},
            json={"username": username, "password": password},
        )

    def delete_test_run(self, run_id: str) -> httpx.Response:
        if not self.runtime.admin_token:
            raise RuntimeError("未配置 MOCK_ADMIN_TOKEN，无法清理 Test Run")
        return self.client.request_raw(
            "DELETE", f"/api/v1/test-runs/{run_id}",
            headers={"X-Admin-Token": self.runtime.admin_token},
        )

    def post_callback(
        self, url: str, *, headers: dict[str, str], content: bytes
    ) -> httpx.Response:
        return self.client.request_raw("POST", url, headers=headers, content=content)

    def mcp_call(self, name: str, arguments: dict, role: str = "employee") -> dict:
        return self.runtime.mcp.call_tool(self.run_id, self.runtime.token(role), name, arguments)

    def current_token(self, role: str = "employee") -> str:
        return self.runtime.token(role)

    def sse_events(self, **kwargs):
        return self.runtime.sse.events(
            self.run_id, self.current_token("employee"), **kwargs
        )

    def websocket_session(self, role: str = "employee"):
        return self.runtime.websocket.session(self.run_id, self.current_token(role))

    def websocket_send(self, socket, payload: dict) -> dict:
        return self.runtime.websocket.send(socket, payload)

    def websocket_receive_type(self, socket, expected_type: str) -> dict:
        return self.runtime.websocket.receive_type(socket, expected_type)

    @staticmethod
    def websocket_rejected(url: str) -> bool:
        try:
            with connect(url, open_timeout=5) as socket:
                socket.recv(timeout=2)
        except Exception:
            return True
        return False

    @property
    def websocket_url(self) -> str:
        return self.runtime.websocket.url

    def mcp_initialize(self, role: str = "employee") -> dict:
        return self.runtime.mcp.initialize(self.run_id, self.current_token(role))

    @property
    def mcp_session_id(self) -> str | None:
        return self.runtime.mcp.session_id

    def mcp_rpc(self, method: str, params: dict | None = None, role: str = "employee"):
        return self.runtime.mcp.rpc(
            self.run_id, self.current_token(role), method, params
        )

    def mcp_rpc_with_session(
        self, session_id: str, method: str, params: dict | None = None,
        role: str = "employee",
    ):
        return self.runtime.mcp.rpc_with_session(
            self.run_id, self.current_token(role), session_id, method, params
        )

    def mcp_cancellation_probe(
        self, name: str, arguments: dict, role: str = "employee"
    ) -> bool:
        return self.runtime.mcp.cancellation_probe(
            self.run_id, self.current_token(role), name, arguments
        )

    def mcp_batch(self, requests: list[dict], role: str = "employee"):
        return self.runtime.mcp.batch(
            self.run_id, self.current_token(role), requests
        )

    def grpc_echo(self, **values):
        return self.runtime.grpc.echo(**values)

    def grpc_incomplete_metadata_code(self, *, missing_run: bool) -> str:
        return self.runtime.grpc.create_claim_without_complete_metadata(
            self.run_id, self.current_token("employee"), missing_run=missing_run
        )

    def grpc_server_stream(self, count: int, interval_ms: int = 0):
        return self.runtime.grpc.server_stream(count, interval_ms)

    def grpc_client_stream(self, values: list[str]):
        return self.runtime.grpc.client_stream(values)

    def grpc_chat(self, count: int):
        return self.runtime.grpc.chat(count)

    def grpc_fail_result(self, status_code: str, message: str):
        return self.runtime.grpc.fail_result(status_code, message)

    def grpc_delay_result(self, seconds: float, value: str, timeout: float):
        return self.runtime.grpc.delay_result(seconds, value, timeout)

    def grpc_versioned_contract(self, version: int):
        return self.runtime.grpc.versioned_contract(version)

    def grpc_start_review(self, contract_name: str, duration: int, risks: int):
        return self.runtime.grpc.start_review(
            self.run_id, self.current_token("employee"), contract_name, duration, risks
        )

    def grpc_get_review(self, job_id: int):
        return self.runtime.grpc.get_review(
            self.run_id, self.current_token("employee"), job_id
        )

    def grpc_watch_review(self, job_id: int):
        return self.runtime.grpc.watch_review(
            self.run_id, self.current_token("employee"), job_id
        )

    def grpc_health_and_services(self):
        return self.runtime.grpc.health_and_services()

    @staticmethod
    def webhook_headers(secret: str, delivery_id: str, body: bytes, timestamp: int | None = None):
        stamp = str(timestamp if timestamp is not None else int(time.time()))
        signature = "sha256=" + hmac.new(
            secret.encode(), stamp.encode() + b"." + body, hashlib.sha256
        ).hexdigest()
        return {
            "Content-Type": "application/json",
            "X-Mango-Delivery-ID": delivery_id,
            "X-Mango-Event": "case.completed",
            "X-Mango-Timestamp": stamp,
            "X-Mango-Signature": signature,
        }

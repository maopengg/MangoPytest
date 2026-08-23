"""三个 API Demo 共用的 Mango Mock 协议客户端。"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from typing import Any, Iterator
from urllib.parse import urlparse

import grpc
import httpx
from grpc_health.v1 import health_pb2, health_pb2_grpc
from grpc_reflection.v1alpha import reflection_pb2, reflection_pb2_grpc
from websockets.sync.client import connect

from auto_tests.common.mango_mock.grpc import mango_mock_pb2 as pb2
from auto_tests.common.mango_mock.grpc import mango_mock_pb2_grpc as pb2_grpc
from core.utils import log


@dataclass(frozen=True)
class HttpResult:
    status_code: int
    body: dict[str, Any]
    headers: dict[str, str]

    @property
    def data(self) -> Any:
        return self.body.get("data")


class HttpProtocolClient:
    def __init__(self, base_url: str, timeout: float = 30):
        self.base_url = base_url.rstrip("/")
        self._client = httpx.Client(timeout=timeout, trust_env=False)

    def close(self) -> None:
        self._client.close()

    @staticmethod
    def headers(run_id: str | None = None, token: str | None = None) -> dict[str, str]:
        result: dict[str, str] = {}
        if run_id:
            result["X-Test-Run-ID"] = run_id
        if token:
            result["Authorization"] = f"Bearer {token}"
        return result

    def request(
        self,
        method: str,
        path: str,
        *,
        run_id: str | None = None,
        token: str | None = None,
        json_data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> HttpResult:
        response = self.request_raw(
            method,
            path,
            run_id=run_id,
            token=token,
            headers=headers,
            json=json_data,
            params=params,
            **kwargs,
        )
        try:
            body = response.json()
        except json.JSONDecodeError:
            body = {"raw": response.text}
        log.debug(f"HTTP {method} {path} -> {response.status_code}")
        return HttpResult(response.status_code, body, dict(response.headers))

    def request_raw(
        self,
        method: str,
        path: str,
        *,
        run_id: str | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """发送原始 HTTP 请求，供需要流、文件或重定向语义的用例使用。"""
        url = path if path.startswith(("http://", "https://")) else (
            f"{self.base_url}/{path.lstrip('/')}"
        )
        return self._client.request(
            method,
            url,
            headers={**self.headers(run_id, token), **(headers or {})},
            **kwargs,
        )

    # 保留 httpx 风格快捷方法，便于功能用例处理文件、回调及临时 Test Run。
    def get(self, path: str, **kwargs: Any) -> httpx.Response:
        return self.request_raw("GET", path, **kwargs)

    def post(self, path: str, **kwargs: Any) -> httpx.Response:
        return self.request_raw("POST", path, **kwargs)

    def put(self, path: str, **kwargs: Any) -> httpx.Response:
        return self.request_raw("PUT", path, **kwargs)

    def patch(self, path: str, **kwargs: Any) -> httpx.Response:
        return self.request_raw("PATCH", path, **kwargs)

    def delete(self, path: str, **kwargs: Any) -> httpx.Response:
        return self.request_raw("DELETE", path, **kwargs)

    def create_run(self, name: str, ttl_minutes: int = 5) -> HttpResult:
        return self.request(
            "POST", "/api/v1/test-runs",
            json_data={"name": name, "tenant_id": "tenant-a", "ttl_minutes": ttl_minutes},
        )

    def delete_run(self, run_id: str, admin_token: str) -> HttpResult:
        return self.request(
            "DELETE", f"/api/v1/test-runs/{run_id}",
            headers={"X-Admin-Token": admin_token},
        )

    def delete_run_with_cleanup_token(
        self, run_id: str, cleanup_token: str
    ) -> HttpResult:
        """使用运行级令牌清理单个 Test Run，不暴露管理员令牌。"""
        return self.request(
            "DELETE", f"/api/v1/test-runs/{run_id}",
            headers={"X-Cleanup-Token": cleanup_token},
        )

    def login(self, run_id: str, username: str, password: str) -> HttpResult:
        return self.request(
            "POST", "/api/v1/auth/login", run_id=run_id,
            json_data={"username": username, "password": password},
        )


class WebSocketProtocolClient:
    def __init__(self, base_url: str):
        parsed = urlparse(base_url)
        scheme = "wss" if parsed.scheme == "https" else "ws"
        self.url = f"{scheme}://{parsed.netloc}/ws"

    def session(self, run_id: str, token: str):
        return connect(
            f"{self.url}?test_run_id={run_id}&token={token}",
            open_timeout=10,
            close_timeout=5,
        )

    @staticmethod
    def send(socket, payload: dict[str, Any]) -> dict[str, Any]:
        socket.send(json.dumps(payload, ensure_ascii=False))
        return json.loads(socket.recv(timeout=10))

    @staticmethod
    def receive_type(socket, expected_type: str, limit: int = 20) -> dict[str, Any]:
        for _ in range(limit):
            message = json.loads(socket.recv(timeout=10))
            if message.get("type") == expected_type:
                return message
        raise AssertionError(f"未收到 WebSocket 消息类型: {expected_type}")


class SseProtocolClient:
    def __init__(self, base_url: str, timeout: float = 15):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def events(
        self,
        run_id: str,
        token: str,
        *,
        topic: str,
        aggregate_id: int | str | None = None,
        last_event_id: int | str | None = None,
        max_events: int = 10,
        end_event: str | None = None,
        fail_after: int | None = None,
        max_duration_seconds: int = 5,
    ) -> list[dict[str, Any]]:
        headers = HttpProtocolClient.headers(run_id, token)
        headers["Accept"] = "text/event-stream"
        if last_event_id is not None:
            headers["Last-Event-ID"] = str(last_event_id)
        params: dict[str, Any] = {
            "topic": topic,
            "max_events": max_events,
            "max_duration_seconds": max_duration_seconds,
            "heartbeat_seconds": 1,
            "interval_ms": 50,
        }
        if aggregate_id is not None:
            params["aggregate_id"] = str(aggregate_id)
        if end_event:
            params["end_event"] = end_event
        if fail_after:
            params["fail_after"] = fail_after
        collected: list[dict[str, Any]] = []
        with httpx.Client(timeout=self.timeout, trust_env=False) as client:
            with client.stream(
                "GET", f"{self.base_url}/api/v1/events/stream",
                headers=headers, params=params,
            ) as response:
                response.raise_for_status()
                current: dict[str, Any] = {}
                data_lines: list[str] = []
                for line in response.iter_lines():
                    if line == "":
                        if current or data_lines:
                            raw = "\n".join(data_lines)
                            try:
                                data = json.loads(raw) if raw else None
                            except json.JSONDecodeError:
                                data = raw
                            event = {**current, "data": data}
                            collected.append(event)
                            if end_event and event.get("event") == end_event:
                                break
                            if len(collected) >= max_events:
                                break
                        current = {}
                        data_lines = []
                        continue
                    if line.startswith(":"):
                        continue
                    field, _, value = line.partition(":")
                    value = value.lstrip()
                    if field == "data":
                        data_lines.append(value)
                    elif field in {"id", "event", "retry"}:
                        current[field] = value
        return collected


class McpProtocolClient:
    def __init__(self, base_url: str, timeout: float = 30):
        self.url = f"{base_url.rstrip('/')}/mcp"
        self._client = httpx.Client(timeout=timeout, trust_env=False)
        self._request_id = 0
        self._session_id: str | None = None

    def close(self) -> None:
        self._client.close()

    @property
    def session_id(self) -> str | None:
        return self._session_id

    def _id(self) -> int:
        self._request_id += 1
        return self._request_id

    def _headers(self, run_id: str, token: str) -> dict[str, str]:
        headers = {
            "Accept": "application/json, text/event-stream",
            "Content-Type": "application/json",
            "MCP-Protocol-Version": "2025-06-18",
            "X-Test-Run-ID": run_id,
            "Authorization": f"Bearer {token}",
        }
        if self._session_id:
            headers["Mcp-Session-Id"] = self._session_id
        return headers

    def initialize(self, run_id: str, token: str) -> dict[str, Any]:
        payload = {
            "jsonrpc": "2.0", "id": self._id(), "method": "initialize",
            "params": {
                "protocolVersion": "2025-06-18",
                "capabilities": {},
                "clientInfo": {"name": "mango-pytest-bdd", "version": "1.0"},
            },
        }
        response = self._client.post(self.url, headers=self._headers(run_id, token), json=payload)
        response.raise_for_status()
        self._session_id = response.headers.get("mcp-session-id")
        result = response.json()
        notify = {"jsonrpc": "2.0", "method": "notifications/initialized"}
        initialized = self._client.post(
            self.url, headers=self._headers(run_id, token), json=notify
        )
        if initialized.status_code not in {200, 202, 204}:
            initialized.raise_for_status()
        return result

    def call_tool(
        self, run_id: str, token: str, name: str, arguments: dict[str, Any]
    ) -> dict[str, Any]:
        if not self._session_id:
            self.initialize(run_id, token)
        payload = {
            "jsonrpc": "2.0", "id": self._id(), "method": "tools/call",
            "params": {"name": name, "arguments": arguments},
        }
        response = self._client.post(self.url, headers=self._headers(run_id, token), json=payload)
        response.raise_for_status()
        rpc = response.json()
        if "error" in rpc:
            return {"isError": True, "error": rpc["error"]}
        result = rpc.get("result", {})
        structured = result.get("structuredContent")
        if isinstance(structured, dict):
            result["value"] = structured
            return result
        for content in result.get("content", []):
            if content.get("type") == "text":
                try:
                    result["value"] = json.loads(content.get("text", ""))
                except json.JSONDecodeError:
                    result["value"] = content.get("text")
                break
        return result

    def rpc(
        self,
        run_id: str,
        token: str,
        method: str,
        params: dict[str, Any] | None = None,
    ) -> tuple[int, Any, dict[str, str]]:
        if method != "initialize" and not self._session_id:
            self.initialize(run_id, token)
        payload = {"jsonrpc": "2.0", "id": self._id(), "method": method}
        if params is not None:
            payload["params"] = params
        response = self._client.post(
            self.url,
            headers=self._headers(run_id, token),
            json=payload,
        )
        body = response.json() if response.content else None
        return response.status_code, body, dict(response.headers)

    def batch(
        self, run_id: str, token: str, requests: list[dict[str, Any]]
    ) -> tuple[int, Any]:
        if not self._session_id:
            self.initialize(run_id, token)
        response = self._client.post(
            self.url,
            headers=self._headers(run_id, token),
            json=requests,
        )
        return response.status_code, response.json() if response.content else None

    def rpc_with_session(
        self,
        run_id: str,
        token: str,
        session_id: str,
        method: str,
        params: dict[str, Any] | None = None,
    ) -> tuple[int, Any, dict[str, str]]:
        original = self._session_id
        self._session_id = session_id
        try:
            return self.rpc(run_id, token, method, params)
        finally:
            self._session_id = original

    def cancellation_probe(
        self,
        run_id: str,
        token: str,
        name: str,
        arguments: dict[str, Any],
        timeout: float = 0.1,
    ) -> bool:
        if not self._session_id:
            self.initialize(run_id, token)
        payload = {
            "jsonrpc": "2.0",
            "id": self._id(),
            "method": "tools/call",
            "params": {"name": name, "arguments": arguments},
        }
        try:
            with httpx.Client(timeout=timeout, trust_env=False) as client:
                client.post(self.url, headers=self._headers(run_id, token), json=payload)
        except httpx.TimeoutException:
            return True
        return False


class GrpcProtocolClient:
    def __init__(self, host: str):
        self._channel = grpc.insecure_channel(
            host,
            options=(
                ("grpc.max_send_message_length", 32 * 1024 * 1024),
                ("grpc.max_receive_message_length", 32 * 1024 * 1024),
            ),
        )
        self.approval = pb2_grpc.ApprovalServiceStub(self._channel)
        self.review = pb2_grpc.ReviewServiceStub(self._channel)
        self.lab = pb2_grpc.TestLabServiceStub(self._channel)

    def close(self) -> None:
        self._channel.close()

    @staticmethod
    def metadata(run_id: str, token: str) -> tuple[tuple[str, str], ...]:
        return (("x-test-run-id", run_id), ("authorization", f"Bearer {token}"))

    def create_claim(self, run_id: str, token: str, amount: float, reason: str):
        return self.approval.CreateClaim(
            pb2.CreateClaimRequest(amount=amount, reason=reason),
            metadata=self.metadata(run_id, token), timeout=10,
        )

    def act_claim(self, run_id: str, token: str, claim_id: int, decision: str = "approve"):
        return self.approval.ActClaim(
            pb2.ActClaimRequest(claim_id=claim_id, decision=decision, comment="AUTO_BDD"),
            metadata=self.metadata(run_id, token), timeout=10,
        )

    def get_claim(self, run_id: str, token: str, claim_id: int):
        return self.approval.GetClaim(
            pb2.GetClaimRequest(claim_id=claim_id),
            metadata=self.metadata(run_id, token), timeout=10,
        )

    def start_review(
        self, run_id: str, token: str, contract_name: str,
        duration_seconds: int = 5, expected_risk_count: int = 3,
    ):
        return self.review.StartReview(
            pb2.StartReviewRequest(
                contract_name=contract_name,
                duration_seconds=duration_seconds,
                expected_risk_count=expected_risk_count,
            ),
            metadata=self.metadata(run_id, token), timeout=10,
        )

    def get_review(self, run_id: str, token: str, job_id: int):
        return self.review.GetReview(
            pb2.GetReviewRequest(job_id=job_id),
            metadata=self.metadata(run_id, token), timeout=10,
        )

    def echo(self, **values):
        return self.lab.UnaryEcho(pb2.EchoRequest(**values), timeout=5)

    def create_claim_without_complete_metadata(
        self, run_id: str, token: str, *, missing_run: bool
    ) -> str:
        metadata = (
            (("authorization", f"Bearer {token}"),)
            if missing_run
            else (("x-test-run-id", run_id),)
        )
        try:
            self.approval.CreateClaim(
                pb2.CreateClaimRequest(amount=10, reason="AUTO"),
                metadata=metadata,
                timeout=5,
            )
        except grpc.RpcError as error:
            return error.code().name
        return "OK"

    def server_stream(self, count: int, interval_ms: int = 0):
        return self.lab.ServerStream(
            pb2.StreamRequest(count=count, interval_ms=interval_ms), timeout=10
        )

    def client_stream(self, values: list[str]):
        items = (pb2.StreamItem(index=index, value=value) for index, value in enumerate(values, 1))
        return self.lab.ClientStream(items, timeout=5)

    def chat(self, count: int):
        requests = (
            pb2.ChatMessage(sender="bdd", message=str(index), sequence=index)
            for index in range(1, count + 1)
        )
        return self.lab.BidirectionalChat(requests, timeout=10)

    def fail_result(self, status_code: str, message: str) -> tuple[str, str]:
        try:
            self.lab.Fail(pb2.FailRequest(status_code=status_code, message=message), timeout=5)
        except grpc.RpcError as error:
            return error.code().name, error.details()
        return "OK", ""

    def delay_result(self, seconds: float, value: str, timeout: float) -> tuple[str, str]:
        try:
            reply = self.lab.Delay(
                pb2.DelayRequest(seconds=seconds, value=value), timeout=timeout
            )
        except grpc.RpcError as error:
            return error.code().name, ""
        return "OK", reply.value.text

    def versioned_contract(self, version: int) -> dict[str, Any]:
        reply = self.lab.VersionedContract(
            pb2.ContractVersionRequest(version=version), timeout=5
        )
        return json.loads(reply.json_data)

    def watch_review(self, run_id: str, token: str, job_id: int):
        return self.review.WatchReview(
            pb2.GetReviewRequest(job_id=job_id, interval_ms=50),
            metadata=self.metadata(run_id, token),
            timeout=5,
        )

    def health_and_services(self) -> tuple[str, set[str]]:
        health = health_pb2_grpc.HealthStub(self._channel).Check(
            health_pb2.HealthCheckRequest(service=""), timeout=5
        )
        replies = reflection_pb2_grpc.ServerReflectionStub(
            self._channel
        ).ServerReflectionInfo(
            iter([reflection_pb2.ServerReflectionRequest(list_services="")]),
            timeout=5,
        )
        names = {
            service.name
            for service in next(replies).list_services_response.service
        }
        status = health_pb2.HealthCheckResponse.ServingStatus.Name(health.status)
        return status, names

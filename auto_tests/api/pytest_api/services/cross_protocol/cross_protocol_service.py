"""跨协议域 L4 Workflow，集中编排 HTTP、WebSocket、MCP、gRPC 和 SSE。"""

from __future__ import annotations

from dataclasses import dataclass

import grpc

from auto_tests.api.pytest_api.data_factory.factories.cross_protocol_factory import (
    CrossProtocolFactory,
)
from auto_tests.api.pytest_api.repositories.cross_protocol import CrossProtocolRepository


@dataclass
class CrossProtocolResult:
    response: object
    checks: dict[str, bool]


class CrossProtocolService:
    APPROVED_STATES = ["finance_pending", "ceo_pending", "approved"]

    def __init__(
        self,
        repository: CrossProtocolRepository,
        factory: CrossProtocolFactory,
        entity,
    ):
        self.repository = repository
        self.factory = factory
        self.entity = entity

    def websocket_single_approval(self) -> CrossProtocolResult:
        claim = self.factory.create_claim_http(self.entity)
        result = self.repository.approve_websocket(claim["id"], "dept_manager")
        return self._claim_result(
            claim["id"], websocket_advanced=result["status"] == "finance_pending"
        )

    def mcp_full_approval(self) -> CrossProtocolResult:
        claim = self.factory.create_claim_mcp(self.entity)
        states = [
            self.repository.act_claim_mcp(claim["id"], role)["status"]
            for role in ("dept_manager", "finance_manager", "ceo")
        ]
        return self._claim_result(claim["id"], mcp_sequence=states == self.APPROVED_STATES)

    def grpc_full_approval(self) -> CrossProtocolResult:
        claim = self.factory.create_claim_grpc(self.entity)
        states = [
            self.repository.act_claim_grpc(claim.claim_id, role).status
            for role in ("dept_manager", "finance_manager", "ceo")
        ]
        return self._claim_result(claim.claim_id, grpc_sequence=states == self.APPROVED_STATES)

    def websocket_full_approval(self) -> CrossProtocolResult:
        claim = self.factory.create_claim_http(self.entity)
        states = [
            self.repository.approve_websocket(claim["id"], role)["status"]
            for role in ("dept_manager", "finance_manager", "ceo")
        ]
        return self._claim_result(
            claim["id"], websocket_sequence=states == self.APPROVED_STATES
        )

    def mcp_create_grpc_approve(self) -> CrossProtocolResult:
        claim = self.factory.create_claim_mcp(self.entity)
        states = [
            self.repository.act_claim_grpc(claim["id"], role).status
            for role in ("dept_manager", "finance_manager", "ceo")
        ]
        return self._claim_result(
            claim["id"], mcp_to_grpc_sequence=states == self.APPROVED_STATES
        )

    def http_review_observed_by_sse(self) -> CrossProtocolResult:
        review = self.factory.start_review_http(self.entity)
        events = self.repository.sse_events(
            topic="review", aggregate_id=review["id"], max_events=100,
            end_event="review.completed", max_duration_seconds=8,
        )
        business = [event for event in events if event.get("event") != "heartbeat"]
        response = self.repository.get_review_http(review["id"])
        return CrossProtocolResult(
            response,
            {
                "sse_has_business_events": bool(business),
                "sse_completed": bool(business) and business[-1]["event"] == "review.completed",
            },
        )

    def grpc_review_cancelled_by_mcp(self) -> CrossProtocolResult:
        review = self.factory.start_review_grpc(self.entity)
        cancelled = self.repository.cancel_review_mcp(review.job_id)
        response = self.repository.get_review_http(review.job_id)
        return CrossProtocolResult(
            response, {"mcp_cancelled": cancelled["status"] == "cancelled"}
        )

    def compare_sse_and_websocket_event(self) -> CrossProtocolResult:
        claim = self.factory.create_claim_http(self.entity)
        sse = self.repository.sse_events(
            topic="approval", aggregate_id=claim["id"],
            max_events=1, max_duration_seconds=3,
        )[0]
        websocket = self.repository.websocket_event(
            topic="approval", aggregate_id=claim["id"], after_id=0
        )
        return self._claim_result(
            claim["id"],
            event_id=int(sse["id"]) == int(websocket["id"]),
            event_payload=sse["data"]["payload"] == websocket["payload"],
            aggregate_id=sse["data"]["aggregate_id"] == websocket["aggregate_id"],
        )

    def replay_websocket_event(self) -> CrossProtocolResult:
        claim = self.factory.create_claim_http(self.entity)
        first = self.repository.websocket_event(
            topic="approval", aggregate_id=claim["id"], after_id=0
        )
        self.repository.act_claim_http(claim["id"], "dept_manager")
        second = self.repository.websocket_event(
            topic="approval", aggregate_id=claim["id"], after_id=int(first["id"])
        )
        return self._claim_result(
            claim["id"],
            cursor_advanced=int(second["id"]) > int(first["id"]),
            approval_replayed=second["event"] == "claim.approved",
        )

    def resume_sse_after_mcp(self) -> CrossProtocolResult:
        claim = self.factory.create_claim_http(self.entity)
        first = self.repository.sse_events(
            topic="approval", aggregate_id=claim["id"],
            max_events=1, max_duration_seconds=3,
        )[0]
        self.repository.act_claim_mcp(claim["id"], "dept_manager")
        second = self.repository.sse_events(
            topic="approval", aggregate_id=claim["id"], last_event_id=first["id"],
            max_events=1, max_duration_seconds=3,
        )[0]
        return self._claim_result(
            claim["id"],
            cursor_advanced=int(second["id"]) > int(first["id"]),
            approval_resumed=second["event"] == "claim.approved",
        )

    def verify_run_isolation(
        self, other: CrossProtocolRepository
    ) -> CrossProtocolResult:
        other_factory = CrossProtocolFactory(other)
        claim_a = self.factory.create_claim_http(self.entity)
        claim_b = other_factory.create_claim_http(self.entity)
        own_mcp = self.repository.get_claim_mcp(claim_a["id"])
        own_grpc = other.get_claim_grpc(claim_b["id"])
        cross_http = self.repository.get_claim_http(claim_b["id"])
        cross_mcp = other.get_claim_mcp(claim_a["id"])
        grpc_isolated = False
        try:
            self.repository.get_claim_grpc(claim_b["id"])
        except grpc.RpcError as error:
            grpc_isolated = error.code() == grpc.StatusCode.NOT_FOUND
        return self._claim_result(
            claim_a["id"], own_mcp=not own_mcp.get("isError"),
            own_grpc=own_grpc.claim_id == claim_b["id"],
            cross_http=cross_http.status_code == 404,
            cross_mcp=bool(cross_mcp.get("isError")), cross_grpc=grpc_isolated,
        )

    def _claim_result(self, claim_id: int, **checks: bool) -> CrossProtocolResult:
        return CrossProtocolResult(self.repository.get_claim_http(claim_id), checks)

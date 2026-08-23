"""跨协议业务动作步骤。"""

from __future__ import annotations

import grpc
from pytest_bdd import then, when


def _record_checks(context: dict, **checks: bool) -> None:
    context.setdefault("checks", {}).update(checks)


@when("部门经理通过 WebSocket 审批报销")
def approve_department_by_websocket(cross_protocol_repository, scenario_context):
    result = cross_protocol_repository.approve_websocket(
        scenario_context["claim_id"], "dept_manager"
    )
    scenario_context["transport_result"] = result
    _record_checks(
        scenario_context,
        websocket_advanced_to_finance=result["status"] == "finance_pending",
    )


@when("按角色顺序通过 MCP 完成全部审批")
def approve_all_by_mcp(cross_protocol_repository, scenario_context):
    claim_id = scenario_context["claim_id"]
    states = [
        cross_protocol_repository.act_claim_mcp(claim_id, "dept_manager")["status"],
        cross_protocol_repository.act_claim_mcp(claim_id, "finance_manager")["status"],
        cross_protocol_repository.act_claim_mcp(claim_id, "ceo")["status"],
    ]
    scenario_context["transport_result"] = states
    _record_checks(
        scenario_context,
        mcp_approval_sequence=states == ["finance_pending", "ceo_pending", "approved"],
    )


@when("按角色顺序通过 gRPC 完成全部审批")
def approve_all_by_grpc(cross_protocol_repository, scenario_context):
    claim_id = scenario_context["claim_id"]
    replies = [
        cross_protocol_repository.act_claim_grpc(claim_id, "dept_manager"),
        cross_protocol_repository.act_claim_grpc(claim_id, "finance_manager"),
        cross_protocol_repository.act_claim_grpc(claim_id, "ceo"),
    ]
    states = [item.status for item in replies]
    scenario_context["transport_result"] = states
    _record_checks(
        scenario_context,
        grpc_approval_sequence=states == ["finance_pending", "ceo_pending", "approved"],
    )


@when("按角色顺序通过 WebSocket 完成全部审批")
def approve_all_by_websocket(cross_protocol_repository, scenario_context):
    claim_id = scenario_context["claim_id"]
    states = [
        cross_protocol_repository.approve_websocket(claim_id, "dept_manager")["status"],
        cross_protocol_repository.approve_websocket(claim_id, "finance_manager")["status"],
        cross_protocol_repository.approve_websocket(claim_id, "ceo")["status"],
    ]
    scenario_context["transport_result"] = states
    _record_checks(
        scenario_context,
        websocket_approval_sequence=states == ["finance_pending", "ceo_pending", "approved"],
    )


@when("通过 gRPC 完成 MCP 创建报销的全部审批")
def approve_mcp_claim_by_grpc(cross_protocol_repository, scenario_context):
    approve_all_by_grpc(cross_protocol_repository, scenario_context)


@when("通过 SSE 观察合同审查直至完成")
def watch_review_by_sse(cross_protocol_repository, scenario_context):
    events = cross_protocol_repository.sse_events(
        topic="review",
        aggregate_id=scenario_context["job_id"],
        max_events=100,
        end_event="review.completed",
        max_duration_seconds=8,
    )
    business_events = [item for item in events if item.get("event") != "heartbeat"]
    scenario_context["transport_result"] = business_events
    _record_checks(
        scenario_context,
        sse_has_business_events=bool(business_events),
        sse_ends_with_review_completed=(
            bool(business_events) and business_events[-1]["event"] == "review.completed"
        ),
    )


@when("通过 MCP 取消 gRPC 创建的合同审查")
def cancel_grpc_review_by_mcp(cross_protocol_repository, scenario_context):
    result = cross_protocol_repository.cancel_review_mcp(scenario_context["job_id"])
    scenario_context["transport_result"] = result
    _record_checks(scenario_context, mcp_cancelled_review=result["status"] == "cancelled")


@when("分别通过 SSE 和 WebSocket 读取同一审批事件")
def read_same_event(cross_protocol_repository, scenario_context):
    claim_id = scenario_context["claim_id"]
    sse_event = cross_protocol_repository.sse_events(
        topic="approval", aggregate_id=claim_id, max_events=1, max_duration_seconds=3
    )[0]
    ws_event = cross_protocol_repository.websocket_event(
        topic="approval", aggregate_id=claim_id, after_id=0
    )
    sse_data = sse_event["data"]
    scenario_context["transport_result"] = {"sse": sse_data, "websocket": ws_event}
    _record_checks(
        scenario_context,
        event_id_consistent=int(sse_event["id"]) == int(ws_event["id"]),
        event_payload_consistent=sse_data["payload"] == ws_event["payload"],
        event_aggregate_consistent=sse_data["aggregate_id"] == ws_event["aggregate_id"],
    )


@when("WebSocket 断线期间通过 HTTP 产生事件后按游标重连")
def replay_websocket_events(cross_protocol_repository, scenario_context):
    claim_id = scenario_context["claim_id"]
    first = cross_protocol_repository.websocket_event(
        topic="approval", aggregate_id=claim_id, after_id=0
    )
    cross_protocol_repository.act_claim_http(claim_id, "dept_manager")
    second = cross_protocol_repository.websocket_event(
        topic="approval", aggregate_id=claim_id, after_id=int(first["id"])
    )
    scenario_context["transport_result"] = [first, second]
    _record_checks(
        scenario_context,
        websocket_cursor_advanced=int(second["id"]) > int(first["id"]),
        websocket_replayed_approval=second["event"] == "claim.approved",
    )


@when("SSE 断线期间通过 MCP 推进审批后按 Last-Event-ID 重连")
def resume_sse_after_mcp(cross_protocol_repository, scenario_context):
    claim_id = scenario_context["claim_id"]
    first = cross_protocol_repository.sse_events(
        topic="approval", aggregate_id=claim_id, max_events=1, max_duration_seconds=3
    )[0]
    cross_protocol_repository.act_claim_mcp(claim_id, "dept_manager")
    second = cross_protocol_repository.sse_events(
        topic="approval", aggregate_id=claim_id,
        last_event_id=first["id"], max_events=1, max_duration_seconds=3,
    )[0]
    scenario_context["transport_result"] = [first, second]
    _record_checks(
        scenario_context,
        sse_cursor_advanced=int(second["id"]) > int(first["id"]),
        sse_resumed_approval=second["event"] == "claim.approved",
    )


@when("分别跨协议验证两个 Test Run 的数据隔离")
def verify_cross_run_isolation(cross_protocol_repository, scenario_context):
    other = scenario_context["secondary_repository"]
    claim_a = scenario_context["claim_a"]
    claim_b = scenario_context["claim_b"]
    own_mcp = cross_protocol_repository.get_claim_mcp(claim_a["id"])
    own_grpc = other.get_claim_grpc(claim_b["id"])
    cross_http = cross_protocol_repository.get_claim_http(claim_b["id"])
    cross_mcp = other.get_claim_mcp(claim_a["id"])
    grpc_isolated = False
    try:
        cross_protocol_repository.get_claim_grpc(claim_b["id"])
    except grpc.RpcError as error:
        grpc_isolated = error.code() == grpc.StatusCode.NOT_FOUND
    _record_checks(
        scenario_context,
        own_mcp_visible=not own_mcp.get("isError"),
        own_grpc_visible=own_grpc.claim_id == claim_b["id"],
        cross_http_isolated=cross_http.status_code == 404,
        cross_mcp_isolated=bool(cross_mcp.get("isError")),
        cross_grpc_isolated=grpc_isolated,
    )


@then("通过 HTTP 查询最终业务状态")
def query_final_http(cross_protocol_repository, scenario_context):
    if "claim_id" in scenario_context:
        response = cross_protocol_repository.get_claim_http(scenario_context["claim_id"])
    else:
        response = cross_protocol_repository.get_review_http(scenario_context["job_id"])
    scenario_context["api_response"] = response

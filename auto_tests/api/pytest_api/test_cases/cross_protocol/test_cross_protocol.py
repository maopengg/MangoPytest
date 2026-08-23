"""跨协议业务一致性的纯 pytest 用例。"""

import allure
import pytest

from core.dal import expect


pytestmark = [
    pytest.mark.integration,
    pytest.mark.cross_protocol,
    allure.epic("Mango Mock API 自动化"),
    allure.feature("跨协议业务一致性"),
]


def assert_result(result, status: str) -> None:
    expect(result.response.status_code).should("= 200")
    expect(result.response.body).should("code = 0")
    expect(result.response.data["status"]).should(f"= '{status}'")
    failed = [name for name, passed in result.checks.items() if not passed]
    expect(failed).should(".size = 0")


@allure.title("FTAPI-0120 WebSocket 驱动单节点报销审批")
def test_ftapi_0120(cross_protocol_service):
    assert_result(cross_protocol_service.websocket_single_approval(), "finance_pending")


@allure.title("FTAPI-0133 MCP 按角色完成报销审批")
def test_ftapi_0133(cross_protocol_service):
    assert_result(cross_protocol_service.mcp_full_approval(), "approved")


@allure.title("FTAPI-0154 gRPC 完成报销审批")
def test_ftapi_0154(cross_protocol_service):
    assert_result(cross_protocol_service.grpc_full_approval(), "approved")


@allure.title("FTAPI-0158 HTTP 创建并由 WebSocket 完成审批")
def test_ftapi_0158(cross_protocol_service):
    assert_result(cross_protocol_service.websocket_full_approval(), "approved")


@allure.title("FTAPI-0159 MCP 创建并由 gRPC 完成审批")
def test_ftapi_0159(cross_protocol_service):
    assert_result(cross_protocol_service.mcp_create_grpc_approve(), "approved")


@allure.title("FTAPI-0160 HTTP 启动审查并通过 SSE 观察进度")
def test_ftapi_0160(cross_protocol_service):
    assert_result(cross_protocol_service.http_review_observed_by_sse(), "completed")


@allure.title("FTAPI-0161 gRPC 启动审查并通过 MCP 取消")
def test_ftapi_0161(cross_protocol_service):
    assert_result(cross_protocol_service.grpc_review_cancelled_by_mcp(), "cancelled")


@allure.title("FTAPI-0162 SSE 与 WebSocket 读取同一业务事件")
def test_ftapi_0162(cross_protocol_service):
    assert_result(cross_protocol_service.compare_sse_and_websocket_event(), "dept_pending")


@allure.title("FTAPI-0163 WebSocket 断线事件重放")
def test_ftapi_0163(cross_protocol_service):
    assert_result(cross_protocol_service.replay_websocket_event(), "finance_pending")


@allure.title("FTAPI-0164 SSE 断线后续传 MCP 事件")
def test_ftapi_0164(cross_protocol_service):
    assert_result(cross_protocol_service.resume_sse_after_mcp(), "finance_pending")


@allure.title("FTAPI-0165 两个 Test Run 的跨协议数据隔离")
def test_ftapi_0165(cross_protocol_service, secondary_repository):
    assert_result(
        cross_protocol_service.verify_run_isolation(secondary_repository),
        "dept_pending",
    )

"""Excel FTAPI-0120/0133/0154/0158-0165 的 BDD 绑定。"""

import allure
import pytest
from pytest_bdd import scenario


pytestmark = [
    pytest.mark.integration,
    pytest.mark.cross_protocol,
    allure.epic("Mango Mock API 自动化"),
    allure.feature("跨协议业务一致性"),
]

FEATURE = "../../features/cross_protocol/cross_protocol.feature"


@allure.title("FTAPI-0120 WebSocket 驱动单节点报销审批")
@scenario(FEATURE, "FTAPI-0120 WebSocket 驱动单节点报销审批")
def test_ftapi_0120():
    pass


@allure.title("FTAPI-0133 MCP 按角色完成报销审批")
@scenario(FEATURE, "FTAPI-0133 MCP 按角色完成报销审批")
def test_ftapi_0133():
    pass


@allure.title("FTAPI-0154 gRPC 完成报销审批")
@scenario(FEATURE, "FTAPI-0154 gRPC 完成报销审批")
def test_ftapi_0154():
    pass


@allure.title("FTAPI-0158 HTTP 创建并由 WebSocket 完成审批")
@scenario(FEATURE, "FTAPI-0158 HTTP 创建并由 WebSocket 完成审批")
def test_ftapi_0158():
    pass


@allure.title("FTAPI-0159 MCP 创建并由 gRPC 完成审批")
@scenario(FEATURE, "FTAPI-0159 MCP 创建并由 gRPC 完成审批")
def test_ftapi_0159():
    pass


@allure.title("FTAPI-0160 HTTP 启动审查并通过 SSE 观察进度")
@scenario(FEATURE, "FTAPI-0160 HTTP 启动审查并通过 SSE 观察进度")
def test_ftapi_0160():
    pass


@allure.title("FTAPI-0161 gRPC 启动审查并通过 MCP 取消")
@scenario(FEATURE, "FTAPI-0161 gRPC 启动审查并通过 MCP 取消")
def test_ftapi_0161():
    pass


@allure.title("FTAPI-0162 SSE 与 WebSocket 读取同一业务事件")
@scenario(FEATURE, "FTAPI-0162 SSE 与 WebSocket 读取同一业务事件")
def test_ftapi_0162():
    pass


@allure.title("FTAPI-0163 WebSocket 断线事件重放")
@scenario(FEATURE, "FTAPI-0163 WebSocket 断线事件重放")
def test_ftapi_0163():
    pass


@allure.title("FTAPI-0164 SSE 断线后续传 MCP 事件")
@scenario(FEATURE, "FTAPI-0164 SSE 断线后续传 MCP 事件")
def test_ftapi_0164():
    pass


@allure.title("FTAPI-0165 两个 Test Run 的跨协议数据隔离")
@scenario(FEATURE, "FTAPI-0165 两个 Test Run 的跨协议数据隔离")
def test_ftapi_0165():
    pass

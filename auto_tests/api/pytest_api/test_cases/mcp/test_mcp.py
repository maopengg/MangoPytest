"""MCP 纯 pytest 协议用例。"""
import allure
import pytest

pytestmark = [pytest.mark.integration, pytest.mark.mcp, allure.epic("Mango Mock API 自动化"), allure.feature("MCP")]
CASES = [
    ("FTAPI-0122 发送 initialize 请求建立 MCP 会话", "initialize_session"),
    ("FTAPI-0123 不携带有效会话标识调用受会话约束的方法", "reject_invalid_session"),
    ("FTAPI-0124 查询 tools、resources 和 prompts 能力清单", "list_capabilities"),
    ("FTAPI-0125 调用 echo_json_types 工具传入完整 JSON 类型矩阵", "echo_json_types"),
    ("FTAPI-0126 调用 delayed_tool 并设置合法短延迟", "delayed_tool"),
    ("FTAPI-0127 调用 delayed_tool 并让客户端提前取消", "cancel_delayed_tool"),
    ("FTAPI-0128 调用 raise_business_error 工具", "business_error"),
    ("FTAPI-0129 请求 large_tool_result 的最小和最大允许条数", "large_tool_result"),
    ("FTAPI-0130 启动 progressive_task 并接收进度和日志通知", "progressive_task"),
    ("FTAPI-0131 取消正在执行的 progressive_task", "cancel_progressive_task"),
    ("FTAPI-0132 使用 create_expense_claim 创建报销并查询工作流资源", "create_claim_and_read_resource"),
    ("FTAPI-0134 启动合同审查并通过 MCP 查询审查进度", "query_contract_review"),
    ("FTAPI-0135 取消运行中的合同审查", "cancel_contract_review"),
    ("FTAPI-0136 读取 mock 二进制资源的最小和最大允许大小", "read_binary_resources"),
    ("FTAPI-0137 渲染 approval_summary Prompt", "render_approval_prompt"),
    ("FTAPI-0138 使用 JSON-RPC batch 混合成功、失败和通知请求", "mixed_jsonrpc_batch"),
    ("FTAPI-0139 调用 cleanup_test_run 时使用无效管理员令牌", "reject_cleanup_without_admin"),
]

@pytest.mark.parametrize(("title", "method_name"), CASES, ids=[title.split()[0] for title, _ in CASES])
def test_mcp_case(title, method_name, mcp_service, assert_scenario):
    allure.dynamic.title(title)
    assert_scenario(getattr(mcp_service, method_name)())

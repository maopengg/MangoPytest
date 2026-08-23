"""gRPC 纯 pytest 协议用例。"""
import allure
import pytest

pytestmark = [pytest.mark.integration, pytest.mark.grpc, allure.epic("Mango Mock API 自动化"), allure.feature("gRPC")]
CASES = [
    ("FTAPI-0140 调用 UnaryEcho 发送标准 Protobuf 消息", "unary_echo"),
    ("FTAPI-0141 调用 UnaryEcho 发送空字符串和 Unicode", "echo_unicode_and_empty"),
    ("FTAPI-0142 缺少 x-test-run-id 元数据调用业务服务", "reject_missing_run_metadata"),
    ("FTAPI-0143 缺少或使用无效 authorization 元数据调用业务服务", "reject_missing_auth_metadata"),
    ("FTAPI-0144 调用 ServerStream 接收指定数量消息", "server_stream"),
    ("FTAPI-0145 在 ServerStream 中途由客户端取消调用", "cancel_server_stream"),
    ("FTAPI-0146 向 ClientStream 连续发送多条消息后关闭发送端", "client_stream"),
    ("FTAPI-0147 向 ClientStream 发送零条消息后关闭发送端", "empty_client_stream"),
    ("FTAPI-0148 通过 BidirectionalChat 交错发送和接收多条消息", "bidirectional_chat"),
    ("FTAPI-0149 为 BidirectionalChat 制造慢消费者", "slow_bidirectional_chat"),
    ("FTAPI-0150 调用 Fail 触发预置 gRPC 错误码", "expected_error"),
    ("FTAPI-0151 调用 Delay 并设置短于客户端截止时间的延迟", "delay_within_deadline"),
    ("FTAPI-0152 调用 Delay 并设置长于客户端截止时间的延迟", "deadline_exceeded_and_recover"),
    ("FTAPI-0153 调用 VersionedContract 的版本 1 和版本 2", "versioned_contract"),
    ("FTAPI-0155 使用 ReviewService 启动并查询合同审查", "start_and_query_review"),
    ("FTAPI-0156 订阅 WatchReview 服务端流直至审查终态", "watch_review"),
    ("FTAPI-0157 调用标准 gRPC Health 和 Reflection 服务", "health_and_reflection"),
]

@pytest.mark.parametrize(("title", "method_name"), CASES, ids=[title.split()[0] for title, _ in CASES])
def test_grpc_case(title, method_name, grpc_service, assert_scenario):
    allure.dynamic.title(title)
    assert_scenario(getattr(grpc_service, method_name)())

"""SSE 纯 pytest 协议用例。"""
import allure
import pytest

pytestmark = [pytest.mark.integration, pytest.mark.sse, allure.epic("Mango Mock API 自动化"), allure.feature("事件流")]
CASES = [
    ("FTAPI-0096 订阅有限条数的标准 SSE 事件流", "finite_standard_stream"),
    ("FTAPI-0097 验证 SSE 事件的 id、event 和 data 字段", "standard_event_fields"),
    ("FTAPI-0098 订阅包含心跳的 SSE 事件流", "heartbeat_stream"),
    ("FTAPI-0099 携带 Last-Event-ID 重新连接事件流", "reconnect_with_last_event_id"),
    ("FTAPI-0100 在指定事件后由服务主动断开连接", "server_closes_after_event"),
    ("FTAPI-0101 断开后自动重连并完成剩余事件消费", "resume_remaining_events"),
    ("FTAPI-0102 消费包含多行 data 的 SSE 原始事件", "multiline_data"),
    ("FTAPI-0103 消费包含注释、BOM 和分块边界的 SSE 原始流", "comments_bom_and_partial_chunks"),
    ("FTAPI-0104 消费在指定位置产生畸形事件的 SSE Lab", "malformed_event_recovery"),
    ("FTAPI-0105 请求返回 204 的 SSE 停止模式", "stop_with_no_content"),
]

@pytest.mark.parametrize(("title", "method_name"), CASES, ids=[title.split()[0] for title, _ in CASES])
def test_sse_case(title, method_name, sse_service, assert_scenario):
    allure.dynamic.title(title)
    assert_scenario(getattr(sse_service, method_name)())

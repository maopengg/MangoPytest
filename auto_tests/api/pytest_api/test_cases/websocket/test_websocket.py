"""WebSocket 纯 pytest 协议用例。"""
import allure
import pytest

pytestmark = [pytest.mark.integration, pytest.mark.websocket, allure.epic("Mango Mock API 自动化"), allure.feature("双向通信")]
CASES = [
    ("FTAPI-0106 携带有效 Test Run 和 Token 建立 WebSocket 连接", "connect_with_credentials"),
    ("FTAPI-0107 缺少 Test Run 标识建立 WebSocket 连接", "reject_missing_run"),
    ("FTAPI-0108 缺少或使用无效 Token 建立 WebSocket 连接", "reject_invalid_token"),
    ("FTAPI-0109 发送 ping 动作", "ping_pong"),
    ("FTAPI-0110 发送包含嵌套 JSON 和 Unicode 的 echo 动作", "echo_json"),
    ("FTAPI-0111 发送二进制帧", "echo_binary"),
    ("FTAPI-0112 发送无法解析的 JSON 文本帧", "reject_invalid_json"),
    ("FTAPI-0113 发送未知 action", "reject_unknown_action"),
    ("FTAPI-0114 订阅主题后触发对应业务事件", "subscribe_business_event"),
    ("FTAPI-0115 缺少 topic 发送订阅动作", "reject_missing_topic"),
    ("FTAPI-0116 取消订阅后再次触发对应业务事件", "unsubscribe_topic"),
    ("FTAPI-0117 断线后携带 after_id 恢复主题订阅", "resume_subscription"),
    ("FTAPI-0118 请求 burst 大量消息并校验序号", "receive_burst"),
    ("FTAPI-0119 模拟慢消费者接收大量消息", "tolerate_slow_consumer"),
    ("FTAPI-0121 请求服务端主动 close", "server_close"),
]

@pytest.mark.parametrize(("title", "method_name"), CASES, ids=[title.split()[0] for title, _ in CASES])
def test_websocket_case(title, method_name, websocket_service, assert_scenario):
    allure.dynamic.title(title)
    assert_scenario(getattr(websocket_service, method_name)())

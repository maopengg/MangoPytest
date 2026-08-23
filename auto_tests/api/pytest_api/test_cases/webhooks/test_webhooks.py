"""Webhook 域纯 pytest 用例。"""
import allure
import pytest

pytestmark = [pytest.mark.integration, pytest.mark.webhook, allure.epic("Mango Mock API 自动化"), allure.feature("Webhook")]
CASES = [
    ("FTAPI-0088 向正常 Receiver 投递带签名的 Webhook", "deliver_signed_webhook"),
    ("FTAPI-0089 Receiver 首次失败后由投递端自动重试", "retry_once_then_succeed"),
    ("FTAPI-0090 Receiver 持续失败直至耗尽最大重试次数", "exhaust_retries"),
    ("FTAPI-0091 向 Receiver 发送签名被篡改的请求", "reject_tampered_signature"),
    ("FTAPI-0092 向 Receiver 发送时间戳过期的签名请求", "reject_expired_signature"),
    ("FTAPI-0093 重复投递相同事件标识", "accept_duplicate_delivery_id"),
    ("FTAPI-0094 投递包含嵌套对象、数组和 Unicode 的载荷", "preserve_complex_payload"),
    ("FTAPI-0095 跨 Test Run 查询 Webhook Delivery 和 Receipt", "enforce_cross_run_isolation"),
]

@pytest.mark.parametrize(("title", "method_name"), CASES, ids=[title.split()[0] for title, _ in CASES])
def test_webhook_case(title, method_name, webhook_service, assert_scenario):
    allure.dynamic.title(title)
    assert_scenario(getattr(webhook_service, method_name)())

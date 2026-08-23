"""Webhook功能用例的 BDD 绑定。"""

import allure
import pytest
from pytest_bdd import scenario


pytestmark = [
    pytest.mark.integration,
    pytest.mark.webhook,
    allure.epic("Mango Mock API 自动化"),
    allure.feature("Webhook"),
]

FEATURE = "../../features/webhooks/webhooks.feature"

@allure.title("FTAPI-0088 向正常 Receiver 投递带签名的 Webhook")
@scenario(FEATURE, "FTAPI-0088 向正常 Receiver 投递带签名的 Webhook")
def test_ftapi_0088():
    pass


@allure.title("FTAPI-0089 Receiver 首次失败后由投递端自动重试")
@scenario(FEATURE, "FTAPI-0089 Receiver 首次失败后由投递端自动重试")
def test_ftapi_0089():
    pass


@allure.title("FTAPI-0090 Receiver 持续失败直至耗尽最大重试次数")
@scenario(FEATURE, "FTAPI-0090 Receiver 持续失败直至耗尽最大重试次数")
def test_ftapi_0090():
    pass


@allure.title("FTAPI-0091 向 Receiver 发送签名被篡改的请求")
@scenario(FEATURE, "FTAPI-0091 向 Receiver 发送签名被篡改的请求")
def test_ftapi_0091():
    pass


@allure.title("FTAPI-0092 向 Receiver 发送时间戳过期的签名请求")
@scenario(FEATURE, "FTAPI-0092 向 Receiver 发送时间戳过期的签名请求")
def test_ftapi_0092():
    pass


@allure.title("FTAPI-0093 重复投递相同事件标识")
@scenario(FEATURE, "FTAPI-0093 重复投递相同事件标识")
def test_ftapi_0093():
    pass


@allure.title("FTAPI-0094 投递包含嵌套对象、数组和 Unicode 的载荷")
@scenario(FEATURE, "FTAPI-0094 投递包含嵌套对象、数组和 Unicode 的载荷")
def test_ftapi_0094():
    pass


@allure.title("FTAPI-0095 跨 Test Run 查询 Webhook Delivery 和 Receipt")
@scenario(FEATURE, "FTAPI-0095 跨 Test Run 查询 Webhook Delivery 和 Receipt")
def test_ftapi_0095():
    pass

"""双向通信功能用例的 BDD 绑定。"""

import allure
import pytest
from pytest_bdd import scenario


pytestmark = [
    pytest.mark.integration,
    pytest.mark.websocket,
    allure.epic("Mango Mock API 自动化"),
    allure.feature("双向通信"),
]

FEATURE = "../../features/websocket/websocket.feature"

@allure.title("FTAPI-0106 携带有效 Test Run 和 Token 建立 WebSocket 连接")
@scenario(FEATURE, "FTAPI-0106 携带有效 Test Run 和 Token 建立 WebSocket 连接")
def test_ftapi_0106():
    pass


@allure.title("FTAPI-0107 缺少 Test Run 标识建立 WebSocket 连接")
@scenario(FEATURE, "FTAPI-0107 缺少 Test Run 标识建立 WebSocket 连接")
def test_ftapi_0107():
    pass


@allure.title("FTAPI-0108 缺少或使用无效 Token 建立 WebSocket 连接")
@scenario(FEATURE, "FTAPI-0108 缺少或使用无效 Token 建立 WebSocket 连接")
def test_ftapi_0108():
    pass


@allure.title("FTAPI-0109 发送 ping 动作")
@scenario(FEATURE, "FTAPI-0109 发送 ping 动作")
def test_ftapi_0109():
    pass


@allure.title("FTAPI-0110 发送包含嵌套 JSON 和 Unicode 的 echo 动作")
@scenario(FEATURE, "FTAPI-0110 发送包含嵌套 JSON 和 Unicode 的 echo 动作")
def test_ftapi_0110():
    pass


@allure.title("FTAPI-0111 发送二进制帧")
@scenario(FEATURE, "FTAPI-0111 发送二进制帧")
def test_ftapi_0111():
    pass


@allure.title("FTAPI-0112 发送无法解析的 JSON 文本帧")
@scenario(FEATURE, "FTAPI-0112 发送无法解析的 JSON 文本帧")
def test_ftapi_0112():
    pass


@allure.title("FTAPI-0113 发送未知 action")
@scenario(FEATURE, "FTAPI-0113 发送未知 action")
def test_ftapi_0113():
    pass


@allure.title("FTAPI-0114 订阅主题后触发对应业务事件")
@scenario(FEATURE, "FTAPI-0114 订阅主题后触发对应业务事件")
def test_ftapi_0114():
    pass


@allure.title("FTAPI-0115 缺少 topic 发送订阅动作")
@scenario(FEATURE, "FTAPI-0115 缺少 topic 发送订阅动作")
def test_ftapi_0115():
    pass


@allure.title("FTAPI-0116 取消订阅后再次触发对应业务事件")
@scenario(FEATURE, "FTAPI-0116 取消订阅后再次触发对应业务事件")
def test_ftapi_0116():
    pass


@allure.title("FTAPI-0117 断线后携带 after_id 恢复主题订阅")
@scenario(FEATURE, "FTAPI-0117 断线后携带 after_id 恢复主题订阅")
def test_ftapi_0117():
    pass


@allure.title("FTAPI-0118 请求 burst 大量消息并校验序号")
@scenario(FEATURE, "FTAPI-0118 请求 burst 大量消息并校验序号")
def test_ftapi_0118():
    pass


@allure.title("FTAPI-0119 模拟慢消费者接收大量消息")
@scenario(FEATURE, "FTAPI-0119 模拟慢消费者接收大量消息")
def test_ftapi_0119():
    pass


@allure.title("FTAPI-0121 请求服务端主动 close")
@scenario(FEATURE, "FTAPI-0121 请求服务端主动 close")
def test_ftapi_0121():
    pass


"""订单域纯 pytest 用例。"""
import allure
import pytest

pytestmark = [pytest.mark.integration, pytest.mark.http, allure.epic("Mango Mock API 自动化"), allure.feature("订单")]

@allure.title("FTAPI-0023 使用有效商品和数量创建订单")
def test_ftapi_0023(order_service, assert_scenario): assert_scenario(order_service.create_valid_order())

@allure.title("FTAPI-0024 使用相同幂等键和相同请求体重复创建订单")
def test_ftapi_0024(order_service, assert_scenario): assert_scenario(order_service.replay_same_idempotency_key())

@allure.title("FTAPI-0025 使用相同幂等键和不同请求体创建订单")
def test_ftapi_0025(order_service, assert_scenario): assert_scenario(order_service.reject_idempotency_conflict())

@allure.title("FTAPI-0026 使用不存在的商品创建订单")
def test_ftapi_0026(order_service, assert_scenario): assert_scenario(order_service.reject_unknown_product())

@allure.title("FTAPI-0027 以数量零创建订单")
def test_ftapi_0027(order_service, assert_scenario): assert_scenario(order_service.reject_zero_quantity())

@allure.title("FTAPI-0028 支付处于待支付状态的订单")
def test_ftapi_0028(order_service, assert_scenario): assert_scenario(order_service.pay_pending_order())

@allure.title("FTAPI-0029 重复支付已支付订单")
def test_ftapi_0029(order_service, assert_scenario): assert_scenario(order_service.reject_duplicate_payment())

@allure.title("FTAPI-0030 退款已支付订单")
def test_ftapi_0030(order_service, assert_scenario): assert_scenario(order_service.refund_paid_order())

@allure.title("FTAPI-0031 退款未支付订单")
def test_ftapi_0031(order_service, assert_scenario): assert_scenario(order_service.reject_refund_before_payment())

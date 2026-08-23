"""订单功能用例的 BDD 绑定。"""

import allure
import pytest
from pytest_bdd import scenario


pytestmark = [
    pytest.mark.integration,
    pytest.mark.http,
    allure.epic("Mango Mock API 自动化"),
    allure.feature("订单"),
]

FEATURE = "../../features/orders/orders.feature"

@allure.title("FTAPI-0023 使用有效商品和数量创建订单")
@scenario(FEATURE, "FTAPI-0023 使用有效商品和数量创建订单")
def test_ftapi_0023():
    pass


@allure.title("FTAPI-0024 使用相同幂等键和相同请求体重复创建订单")
@scenario(FEATURE, "FTAPI-0024 使用相同幂等键和相同请求体重复创建订单")
def test_ftapi_0024():
    pass


@allure.title("FTAPI-0025 使用相同幂等键和不同请求体创建订单")
@scenario(FEATURE, "FTAPI-0025 使用相同幂等键和不同请求体创建订单")
def test_ftapi_0025():
    pass


@allure.title("FTAPI-0026 使用不存在的商品创建订单")
@scenario(FEATURE, "FTAPI-0026 使用不存在的商品创建订单")
def test_ftapi_0026():
    pass


@allure.title("FTAPI-0027 以数量零创建订单")
@scenario(FEATURE, "FTAPI-0027 以数量零创建订单")
def test_ftapi_0027():
    pass


@allure.title("FTAPI-0028 支付处于待支付状态的订单")
@scenario(FEATURE, "FTAPI-0028 支付处于待支付状态的订单")
def test_ftapi_0028():
    pass


@allure.title("FTAPI-0029 重复支付已支付订单")
@scenario(FEATURE, "FTAPI-0029 重复支付已支付订单")
def test_ftapi_0029():
    pass


@allure.title("FTAPI-0030 退款已支付订单")
@scenario(FEATURE, "FTAPI-0030 退款已支付订单")
def test_ftapi_0030():
    pass


@allure.title("FTAPI-0031 退款未支付订单")
@scenario(FEATURE, "FTAPI-0031 退款未支付订单")
def test_ftapi_0031():
    pass


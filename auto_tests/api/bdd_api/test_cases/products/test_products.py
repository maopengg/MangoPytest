"""商品功能用例的 BDD 绑定。"""

import allure
import pytest
from pytest_bdd import scenario


pytestmark = [
    pytest.mark.integration,
    pytest.mark.http,
    allure.epic("Mango Mock API 自动化"),
    allure.feature("商品"),
]

FEATURE = "../../features/products/products.feature"

@allure.title("FTAPI-0015 使用合法且唯一的 SKU 创建商品")
@scenario(FEATURE, "FTAPI-0015 使用合法且唯一的 SKU 创建商品")
def test_ftapi_0015():
    pass


@allure.title("FTAPI-0016 使用已存在的 SKU 再次创建商品")
@scenario(FEATURE, "FTAPI-0016 使用已存在的 SKU 再次创建商品")
def test_ftapi_0016():
    pass


@allure.title("FTAPI-0017 创建价格为零的商品")
@scenario(FEATURE, "FTAPI-0017 创建价格为零的商品")
def test_ftapi_0017():
    pass


@allure.title("FTAPI-0018 创建价格为负数的商品")
@scenario(FEATURE, "FTAPI-0018 创建价格为负数的商品")
def test_ftapi_0018():
    pass


@allure.title("FTAPI-0019 按名称关键字查询商品列表")
@scenario(FEATURE, "FTAPI-0019 按名称关键字查询商品列表")
def test_ftapi_0019():
    pass


@allure.title("FTAPI-0020 携带当前版本号更新商品价格")
@scenario(FEATURE, "FTAPI-0020 携带当前版本号更新商品价格")
def test_ftapi_0020():
    pass


@allure.title("FTAPI-0021 携带过期版本号更新商品")
@scenario(FEATURE, "FTAPI-0021 携带过期版本号更新商品")
def test_ftapi_0021():
    pass


@allure.title("FTAPI-0022 删除已存在的商品后再次查询")
@scenario(FEATURE, "FTAPI-0022 删除已存在的商品后再次查询")
def test_ftapi_0022():
    pass


"""商品域纯 pytest 功能用例。"""

import allure
import pytest

from core.dal import expect


pytestmark = [
    pytest.mark.integration,
    pytest.mark.http,
    allure.epic("Mango Mock API 自动化"),
    allure.feature("商品"),
]


@allure.title("FTAPI-0015 使用合法且唯一的 SKU 创建商品")
def test_ftapi_0015(product_service):
    response = product_service.create()
    expect(response.status_code).should("= 201")
    expect(response.json()).should("code = 0")
    expect(response.json()).should("data.version = 1")


@allure.title("FTAPI-0016 使用已存在的 SKU 再次创建商品")
def test_ftapi_0016(product_service):
    first, second = product_service.create_duplicate()
    expect(first.status_code).should("= 201")
    expect(second.status_code).should("= 409")


@allure.title("FTAPI-0017 创建价格为零的商品")
def test_ftapi_0017(product_service):
    expect(product_service.create(price=0).status_code).should("= 422")


@allure.title("FTAPI-0018 创建价格为负数的商品")
def test_ftapi_0018(product_service):
    expect(product_service.create(price=-0.01).status_code).should("= 422")


@allure.title("FTAPI-0019 按名称关键字查询商品列表")
def test_ftapi_0019(product_service):
    matched, other, response, keyword = product_service.search_by_name()
    expect(matched.status_code).should("= 201")
    expect(other.status_code).should("= 201")
    expect(response.status_code).should("= 200")
    expect(response.json()).should("data.total = 1")
    expect(response.json()).should(
        f"data.items[0].name contains '{keyword}'"
    )


@allure.title("FTAPI-0020 携带当前版本号更新商品价格")
def test_ftapi_0020(product_service):
    created, response = product_service.update_current_version()
    expect(response.status_code).should("= 200")
    expect(response.json()["data"]["version"]).should(f"= {created['version'] + 1}")


@allure.title("FTAPI-0021 携带过期版本号更新商品")
def test_ftapi_0021(product_service):
    first, stale = product_service.update_stale_version()
    expect(first.status_code).should("= 200")
    expect(stale.status_code).should("= 409")
    expect(stale.json()).should("code = 'OPTIMISTIC_LOCK_CONFLICT'")


@allure.title("FTAPI-0022 删除已存在的商品后再次查询")
def test_ftapi_0022(product_service):
    deleted, searched = product_service.delete_then_search()
    expect(deleted.status_code).should("= 200")
    expect(searched.status_code).should("= 200")
    expect(searched.json()).should("data.total = 0")

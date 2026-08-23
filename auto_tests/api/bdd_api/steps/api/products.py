"""商品域 L4 API 操作步骤。"""

from __future__ import annotations

from pytest_bdd import when

from core.utils import log


def _record_response(scenario_context: dict, response):
    body = response.json()
    result = {
        "response": response,
        "status_code": response.status_code,
        "body": body,
        "data": body.get("data"),
    }
    scenario_context["api_response"] = result
    return result


@when("创建该商品", target_fixture="api_response")
def create_product(scenario_context, product_repository):
    log.info("创建商品")
    return _record_response(
        scenario_context,
        product_repository.create(scenario_context["product"]),
    )


@when("使用相同 SKU 再次创建商品", target_fixture="api_response")
def create_duplicate_product(scenario_context, product_factory, product_repository):
    created = scenario_context["created_product"]
    duplicate = product_factory.build(
        sku=created["sku"], name=created["name"]
    )
    return _record_response(scenario_context, product_repository.create(duplicate))


@when("按该名称关键字查询商品", target_fixture="api_response")
def search_products(scenario_context, product_repository):
    return _record_response(
        scenario_context,
        product_repository.search(scenario_context["keyword"]),
    )


@when("携带当前版本号更新商品价格", target_fixture="api_response")
def update_with_current_version(scenario_context, product_repository):
    product = scenario_context["created_product"]
    scenario_context["original_version"] = product["version"]
    return _record_response(
        scenario_context,
        product_repository.update_price(
            product["id"], price=22.5, version=product["version"]
        ),
    )


@when("携带过期版本号更新商品价格", target_fixture="api_response")
def update_with_stale_version(scenario_context, product_repository):
    product = scenario_context["created_product"]
    return _record_response(
        scenario_context,
        product_repository.update_price(
            product["id"], price=33.5, version=scenario_context["stale_version"]
        ),
    )


@when("删除该商品后按 SKU 查询", target_fixture="api_response")
def delete_then_search(scenario_context, product_repository):
    product = scenario_context["created_product"]
    deleted = product_repository.delete(product["id"])
    scenario_context["delete_response"] = deleted
    return _record_response(
        scenario_context, product_repository.search(product["sku"])
    )

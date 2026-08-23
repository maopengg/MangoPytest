"""商品域 L3 数据准备步骤。"""

from pytest_bdd import given

from core.dal import expect
from core.utils import log


def _create_product(scenario_context, product_factory, product_repository, **overrides):
    entity = product_factory.build(**overrides)
    response = product_repository.create(entity)
    expect(response.status_code).should("= 201")
    scenario_context.update(
        product=entity,
        created_product=response.json()["data"],
    )
    log.debug(f"已准备商品: {entity.sku}")


@given("已生成合法且唯一的商品数据")
def valid_product(scenario_context, product_factory):
    scenario_context["product"] = product_factory.build()


@given("已生成价格为零的商品数据")
def zero_price_product(scenario_context, product_factory):
    scenario_context["product"] = product_factory.build(price=0)


@given("已生成价格为负数的商品数据")
def negative_price_product(scenario_context, product_factory):
    scenario_context["product"] = product_factory.build(price=-0.01)


@given("已存在一个商品")
def existing_product(
    scenario_context, product_factory, product_repository
):
    _create_product(scenario_context, product_factory, product_repository)


@given("已存在名称匹配和不匹配关键字的商品")
def searchable_products(
    scenario_context, product_factory, product_repository
):
    keyword = product_factory.unique("AUTO_MATCH")
    _create_product(
        scenario_context,
        product_factory,
        product_repository,
        name=f"{keyword}_PRODUCT",
    )
    other = product_repository.create(product_factory.build())
    expect(other.status_code).should("= 201")
    scenario_context["keyword"] = keyword


@given("商品已使用当前版本成功更新一次")
def updated_product_once(scenario_context, product_repository):
    product = scenario_context["created_product"]
    scenario_context["stale_version"] = product["version"]
    response = product_repository.update_price(
        product["id"], price=22.5, version=product["version"]
    )
    expect(response.status_code).should("= 200")
    scenario_context["first_update"] = response.json()["data"]

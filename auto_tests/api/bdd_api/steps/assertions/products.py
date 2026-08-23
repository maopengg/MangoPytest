"""商品域 L4 DAL 断言步骤。"""

import json

from pytest_bdd import parsers, then

from core.dal import expect
from core.utils import log


@then(parsers.parse("商品响应状态码为 {status_code:d}"))
def assert_product_status(scenario_context, status_code):
    actual = scenario_context["api_response"]["status_code"]
    log.debug(f"验证商品响应状态码: {actual}")
    expect(actual).should(f"= {status_code}")


@then(parsers.parse('商品响应业务 code 为 "{code}"'))
def assert_product_code(scenario_context, code):
    expected = json.loads(code) if code.lstrip("-").isdigit() else code
    expect(scenario_context["api_response"]["body"]["code"]).should(
        f"= {expected!r}"
    )


@then("新商品版本号为 1")
def assert_initial_version(scenario_context):
    expect(scenario_context["api_response"]["data"]["version"]).should("= 1")


@then("查询结果仅包含名称匹配的商品")
def assert_search_result(scenario_context):
    data = scenario_context["api_response"]["data"]
    keyword = scenario_context["keyword"]
    expect(data["total"]).should("= 1")
    expect(data["items"]).should(".size = 1")
    expect(data).should(f"items[0].name contains '{keyword}'")


@then("商品版本号递增 1")
def assert_version_incremented(scenario_context):
    expected = scenario_context["original_version"] + 1
    expect(scenario_context["api_response"]["data"]["version"]).should(
        f"= {expected}"
    )


@then("删除成功且查询结果为空")
def assert_deleted_and_absent(scenario_context):
    expect(scenario_context["delete_response"].status_code).should("= 200")
    expect(scenario_context["api_response"]["data"]["total"]).should("= 0")

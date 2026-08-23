"""功能用例标准化 DAL 断言步骤。"""

from pytest_bdd import parsers, then

from core.dal import expect


@then(parsers.parse("标准化响应状态码为 {status_code:d}"))
def assert_normalized_status(scenario_context, status_code):
    expect(scenario_context["api_response"].status_code).should(f"= {status_code}")


@then(parsers.parse("标准化业务 code 为 {code:d}"))
def assert_normalized_code(scenario_context, code):
    expect(scenario_context["api_response"].code).should(f"= {code}")


@then("所有功能期望均成立")
def assert_all_functional_checks(scenario_context):
    checks = scenario_context["api_response"].checks
    expect(checks).should(".size > 0")
    for check in checks:
        expect(check).should("= true")

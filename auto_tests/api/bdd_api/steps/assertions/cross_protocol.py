"""跨协议结果的 DAL 断言步骤。"""

from pytest_bdd import parsers, then

from core.dal import expect


@then(parsers.parse("最终 HTTP 状态码为 {status_code:d}"))
def assert_http_status(scenario_context, status_code):
    expect(scenario_context["api_response"].status_code).should(f"= {status_code}")


@then(parsers.parse("最终业务 code 为 {code:d}"))
def assert_business_code(scenario_context, code):
    expect(scenario_context["api_response"].body["code"]).should(f"= {code}")


@then(parsers.parse('最终报销状态为 "{status}"'))
def assert_claim_status(scenario_context, status):
    expect(scenario_context["api_response"].data["status"]).should(f"= '{status}'")


@then(parsers.parse('最终审查状态为 "{status}"'))
def assert_review_status(scenario_context, status):
    expect(scenario_context["api_response"].data["status"]).should(f"= '{status}'")


@then("跨协议结果保持一致")
def assert_cross_protocol_consistency(scenario_context):
    checks = scenario_context.get("checks", {})
    expect(checks).should(".size > 0")
    failed = [name for name, passed in checks.items() if not passed]
    expect(failed).should(".size = 0")

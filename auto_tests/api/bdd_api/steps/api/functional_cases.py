"""165 条功能用例的统一执行步骤。"""

from pytest_bdd import parsers, when


@when(parsers.parse('执行功能用例 "{case_id}"'), target_fixture="api_response")
def execute_functional_case(case_id, functional_case_executor, scenario_context):
    result = functional_case_executor.execute(case_id)
    scenario_context["api_response"] = result
    return {
        "response": result,
        "status_code": result.status_code,
        "data": result.details,
    }

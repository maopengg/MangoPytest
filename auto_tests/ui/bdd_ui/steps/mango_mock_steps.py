"""新版 Mango Mock UI 的通用中文 BDD Steps。"""

from pytest_bdd import given, parsers, then, when

from auto_tests.ui.bdd_ui.capabilities.cases import (
    ELEMENT_CASES,
    INVENTORY_CASES,
    OPERATION_CASES,
)
from auto_tests.ui.bdd_ui.capabilities import BddUICasePage

OPERATIONS = {case.case_id: case for case in OPERATION_CASES}
ELEMENTS = {case.case_id: case for case in ELEMENT_CASES}
INVENTORY = {case.case_id: case for case in INVENTORY_CASES}


@given("使用本项目数据工厂准备UI前置条件")
def enable_local_factory(bdd_ui_data_factory, scenario_context):
    scenario_context["factory"] = bdd_ui_data_factory


@when(parsers.parse('执行 mangoautomation 操作用例 "{case_id}"'))
def execute_operation_case(case_id, base_data, scenario_context):
    BddUICasePage(base_data).execute_operation(OPERATIONS[case_id])
    scenario_context["passed"] = True


@when("执行当前分类的 mangoautomation 操作用例")
def execute_current_operation_case(case_id, base_data, scenario_context):
    execute_operation_case(case_id, base_data, scenario_context)


@when(parsers.parse('操作交互控件用例 "{case_id}"'))
def execute_element_case(case_id, base_data, bdd_ui_data_factory, scenario_context):
    page = BddUICasePage(base_data, bdd_ui_data_factory)
    try:
        page.execute_element(ELEMENTS[case_id])
        scenario_context["passed"] = True
    finally:
        page.cleanup_run()


@when("操作当前分类的交互控件用例")
def execute_current_element_case(case_id, base_data, bdd_ui_data_factory, scenario_context):
    execute_element_case(case_id, base_data, bdd_ui_data_factory, scenario_context)


@when(parsers.parse('验证元素定位用例 "{case_id}"'))
def execute_inventory_case(case_id, base_data, scenario_context):
    BddUICasePage(base_data).verify_inventory(INVENTORY[case_id])
    scenario_context["passed"] = True


@when("验证当前页面的元素定位用例")
def execute_current_inventory_case(case_id, base_data, scenario_context):
    execute_inventory_case(case_id, base_data, scenario_context)


@then("BDD UI 用例应该执行成功")
def assert_case_passed(scenario_context):
    assert scenario_context.get("passed") is True

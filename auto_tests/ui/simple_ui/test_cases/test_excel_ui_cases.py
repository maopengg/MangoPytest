"""新版 Mango Mock UI 的 Excel 全覆盖自动化用例。"""

import allure
import pytest

from auto_tests.ui.simple_ui.abstract.excel_case_page import ExcelCasePage
from auto_tests.ui.simple_ui.excel_cases import ELEMENT_CASES, INVENTORY_CASES, OPERATION_CASES


pytestmark = [pytest.mark.integration, pytest.mark.positive]


@allure.epic("Mango Mock UI 自动化")
@allure.feature("mangoautomation 操作方法覆盖")
@pytest.mark.parametrize("operation_case", OPERATION_CASES, ids=lambda case: case.case_id)
def test_mangoautomation_operation_from_excel(base_data, operation_case):
    """逐条执行 Excel 中的 103 个 mangoautomation 同步 Web 方法。"""
    allure.dynamic.title(f"{operation_case.case_id} {operation_case.method} {operation_case.description}")
    page = ExcelCasePage(base_data)
    page.execute_operation(operation_case)


@allure.epic("Mango Mock UI 自动化")
@allure.feature("交互控件逐一操作")
@pytest.mark.parametrize("element_case", ELEMENT_CASES, ids=lambda case: case.case_id)
def test_interactive_element_from_excel(base_data, element_case):
    """逐条操作 Excel 中的 130 个可交互控件。"""
    allure.dynamic.title(f"{element_case.case_id} 操作 {element_case.element_id}")
    page = ExcelCasePage(base_data)
    try:
        page.execute_element(element_case)
    finally:
        page.cleanup_run()


@allure.epic("Mango Mock UI 自动化")
@allure.feature("data-testid 全元素定位验证")
@pytest.mark.parametrize("inventory_case", INVENTORY_CASES, ids=lambda case: case.case_id)
def test_all_element_from_excel(base_data, inventory_case):
    """逐条检查 Excel 中 260 个静态元素 ID 的定位、唯一性和标签。"""
    allure.dynamic.title(f"{inventory_case.case_id} 定位 {inventory_case.element_id}")
    page = ExcelCasePage(base_data)
    page.verify_inventory(inventory_case)

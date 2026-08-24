"""报销审批业务 UI 场景。"""

import allure
import pytest

pytestmark = [pytest.mark.ui, pytest.mark.positive, pytest.mark.claim]


@allure.epic("Mango Mock UI 自动化")
@allure.feature("业务流程")
@allure.story("报销审批")
@allure.id("PYUI-CLAIM-001")
@allure.title("PYUI-CLAIM-001 部门经理审批当前报销节点")
def test_department_manager_approves_current_claim_stage(
    ui_data_factory, ui_repositories, claim_flow, base_data
):
    claim = ui_data_factory.create_claim()
    previous_stage = claim.raw["current_stage"]
    ui_data_factory.bind_browser(base_data, "dept_manager")
    current_stage = claim_flow.approve_current_stage()
    result = ui_repositories.claims.get_result(claim.id)
    assert result.status_code == 200
    assert current_stage == result.data["current_stage"]
    assert current_stage != previous_stage

"""合同评审业务 UI 场景。"""

import allure
import pytest

pytestmark = [pytest.mark.ui, pytest.mark.positive, pytest.mark.review]


@allure.epic("Mango Mock UI 自动化")
@allure.feature("业务流程")
@allure.story("合同评审")
@allure.id("PYUI-REVIEW-001")
@allure.title("PYUI-REVIEW-001 员工取消进行中的合同评审")
def test_employee_cancels_review(
    ui_data_factory, ui_repositories, review_flow, base_data
):
    review = ui_data_factory.create_review(duration_seconds=30)
    ui_data_factory.bind_browser(base_data, "employee")
    assert review_flow.cancel() == "cancelled"
    result = ui_repositories.reviews.get_result(review.id)
    assert result.status_code == 200
    assert result.data["status"] == "cancelled"

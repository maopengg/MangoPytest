"""纯 pytest 业务 UI 场景，不通过统一 Case ID 执行器。"""

import allure
import pytest

pytestmark = [pytest.mark.ui, pytest.mark.positive]


@allure.id("PYUI-ORDER-001")
@pytest.mark.smoke
@pytest.mark.order
def test_employee_pays_pending_order(
    ui_data_factory, ui_repositories, order_flow, base_data
):
    order = ui_data_factory.create_order("pending")
    ui_data_factory.bind_browser(base_data, "employee")

    assert order_flow.pay() == "paid"
    result = ui_repositories.orders.get_result(order.id)
    assert result.status_code == 200
    assert result.data["status"] == "paid"


@allure.id("PYUI-ORDER-002")
@pytest.mark.order
def test_employee_refunds_paid_order(
    ui_data_factory, ui_repositories, order_flow, base_data
):
    order = ui_data_factory.create_order("paid")
    ui_data_factory.bind_browser(base_data, "employee")

    assert order_flow.refund() == "refunded"
    result = ui_repositories.orders.get_result(order.id)
    assert result.status_code == 200
    assert result.data["status"] == "refunded"


@allure.id("PYUI-CLAIM-001")
@pytest.mark.claim
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


@allure.id("PYUI-REVIEW-001")
@pytest.mark.review
def test_employee_cancels_review(
    ui_data_factory, ui_repositories, review_flow, base_data
):
    review = ui_data_factory.create_review(duration_seconds=30)
    ui_data_factory.bind_browser(base_data, "employee")

    assert review_flow.cancel() == "cancelled"
    result = ui_repositories.reviews.get_result(review.id)
    assert result.status_code == 200
    assert result.data["status"] == "cancelled"

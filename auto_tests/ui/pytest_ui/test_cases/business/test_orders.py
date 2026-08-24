"""订单业务 UI 场景。"""

import allure
import pytest

pytestmark = [pytest.mark.ui, pytest.mark.positive, pytest.mark.order]


@allure.epic("Mango Mock UI 自动化")
@allure.feature("业务流程")
@allure.story("订单")
@allure.id("PYUI-ORDER-001")
@allure.title("PYUI-ORDER-001 员工支付待支付订单")
@pytest.mark.smoke
def test_employee_pays_pending_order(
    ui_data_factory, ui_repositories, order_flow, base_data
):
    order = ui_data_factory.create_order("pending")
    ui_data_factory.bind_browser(base_data, "employee")
    assert order_flow.pay() == "paid"
    result = ui_repositories.orders.get_result(order.id)
    assert result.status_code == 200
    assert result.data["status"] == "paid"


@allure.epic("Mango Mock UI 自动化")
@allure.feature("业务流程")
@allure.story("订单")
@allure.id("PYUI-ORDER-002")
@allure.title("PYUI-ORDER-002 员工退款已支付订单")
def test_employee_refunds_paid_order(
    ui_data_factory, ui_repositories, order_flow, base_data
):
    order = ui_data_factory.create_order("paid")
    ui_data_factory.bind_browser(base_data, "employee")
    assert order_flow.refund() == "refunded"
    result = ui_repositories.orders.get_result(order.id)
    assert result.status_code == 200
    assert result.data["status"] == "refunded"

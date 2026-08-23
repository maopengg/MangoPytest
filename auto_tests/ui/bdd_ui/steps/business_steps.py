"""真实业务语义的中文 BDD UI Steps。"""

from pytest_bdd import given, parsers, then, when


@given("存在一个属于当前员工的待支付订单")
def pending_order(bdd_ui_data_factory, order_context):
    order_context.order = bdd_ui_data_factory.create_order("pending")


@given("存在一个属于当前员工的已支付订单")
def paid_order(bdd_ui_data_factory, order_context):
    order_context.order = bdd_ui_data_factory.create_order("paid")


@given("员工已经登录 Mango Mock")
def employee_logged_in(bdd_ui_data_factory, base_data):
    bdd_ui_data_factory.bind_browser(base_data, "employee")


@when("员工在订单页面支付该订单")
def employee_pays(order_flow, order_context):
    order_context.ui_status = order_flow.pay()


@when("员工在订单页面退款该订单")
def employee_refunds(order_flow, order_context):
    order_context.ui_status = order_flow.refund()


@then(parsers.parse('页面订单状态应该为 "{expected}"'))
def ui_order_status(expected, order_context):
    assert order_context.ui_status == expected


@then(parsers.parse('API 查询到的订单状态应该为 "{expected}"'))
def api_order_status(expected, bdd_ui_repositories, order_context):
    result = bdd_ui_repositories.orders.get_result(order_context.order.id)
    assert result.status_code == 200
    assert result.data["status"] == expected


@given("存在一个等待部门经理审批的报销申请")
def pending_claim(bdd_ui_data_factory, claim_context):
    claim_context.claim = bdd_ui_data_factory.create_claim()
    claim_context.previous_stage = claim_context.claim.raw["current_stage"]


@given("部门经理已经登录 Mango Mock")
def department_manager_logged_in(bdd_ui_data_factory, base_data):
    bdd_ui_data_factory.bind_browser(base_data, "dept_manager")


@when("部门经理审批当前报销节点")
def manager_approves(claim_flow, claim_context):
    claim_context.current_stage = claim_flow.approve_current_stage()


@then("页面应该进入下一个审批节点")
def ui_next_claim_stage(claim_context):
    assert claim_context.current_stage
    assert claim_context.current_stage != claim_context.previous_stage


@then("API 查询到的审批节点应该与页面一致")
def api_claim_stage(bdd_ui_repositories, claim_context):
    result = bdd_ui_repositories.claims.get_result(claim_context.claim.id)
    assert result.status_code == 200
    assert result.data["current_stage"] == claim_context.current_stage


@given("存在一个进行中的合同评审")
def running_review(bdd_ui_data_factory, review_context):
    review_context.review = bdd_ui_data_factory.create_review(duration_seconds=30)


@when("员工在评审页面取消该任务")
def employee_cancels_review(review_flow, review_context):
    review_context.ui_status = review_flow.cancel()


@then(parsers.parse('页面评审状态应该为 "{expected}"'))
def ui_review_status(expected, review_context):
    assert review_context.ui_status == expected


@then(parsers.parse('API 查询到的评审状态应该为 "{expected}"'))
def api_review_status(expected, bdd_ui_repositories, review_context):
    result = bdd_ui_repositories.reviews.get_result(review_context.review.id)
    assert result.status_code == 200
    assert result.data["status"] == expected


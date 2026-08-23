"""跨协议认证步骤。"""

from pytest_bdd import given


@given("已登录员工、部门经理、财务经理和总经理")
def login_all_roles(cross_protocol_repository):
    for role in ("employee", "dept_manager", "finance_manager", "ceo"):
        cross_protocol_repository.token(role)


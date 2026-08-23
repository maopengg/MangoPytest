"""报销审批功能用例的 BDD 绑定。"""

import allure
import pytest
from pytest_bdd import scenario


pytestmark = [
    pytest.mark.integration,
    pytest.mark.http,
    allure.epic("Mango Mock API 自动化"),
    allure.feature("报销审批"),
]

FEATURE = "../../features/claims/claims.feature"

@allure.title("FTAPI-0032 employee 提交普通金额报销")
@scenario(FEATURE, "FTAPI-0032 employee 提交普通金额报销")
def test_ftapi_0032():
    pass


@allure.title("FTAPI-0033 employee 提交大额报销并完成部门、财务和 CEO 审批")
@scenario(FEATURE, "FTAPI-0033 employee 提交大额报销并完成部门、财务和 CEO 审批")
def test_ftapi_0033():
    pass


@allure.title("FTAPI-0034 未轮到的角色提前审批报销")
@scenario(FEATURE, "FTAPI-0034 未轮到的角色提前审批报销")
def test_ftapi_0034():
    pass


@allure.title("FTAPI-0035 申请人审批自己提交的报销")
@scenario(FEATURE, "FTAPI-0035 申请人审批自己提交的报销")
def test_ftapi_0035():
    pass


@allure.title("FTAPI-0036 审批人拒绝待处理报销")
@scenario(FEATURE, "FTAPI-0036 审批人拒绝待处理报销")
def test_ftapi_0036():
    pass


@allure.title("FTAPI-0037 对已完成的审批任务再次执行通过")
@scenario(FEATURE, "FTAPI-0037 对已完成的审批任务再次执行通过")
def test_ftapi_0037():
    pass


@allure.title("FTAPI-0038 申请人在审批前撤回报销")
@scenario(FEATURE, "FTAPI-0038 申请人在审批前撤回报销")
def test_ftapi_0038():
    pass


@allure.title("FTAPI-0039 申请人撤回已通过的报销")
@scenario(FEATURE, "FTAPI-0039 申请人撤回已通过的报销")
def test_ftapi_0039():
    pass


@allure.title("FTAPI-0040 非申请人撤回他人报销")
@scenario(FEATURE, "FTAPI-0040 非申请人撤回他人报销")
def test_ftapi_0040():
    pass


@allure.title("FTAPI-0041 查询当前 Test Run 的报销详情和审批任务")
@scenario(FEATURE, "FTAPI-0041 查询当前 Test Run 的报销详情和审批任务")
def test_ftapi_0041():
    pass


@allure.title("FTAPI-0042 跨 Test Run 查询同一报销标识")
@scenario(FEATURE, "FTAPI-0042 跨 Test Run 查询同一报销标识")
def test_ftapi_0042():
    pass


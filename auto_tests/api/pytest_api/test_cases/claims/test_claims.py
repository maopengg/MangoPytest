"""报销审批域纯 pytest 用例。"""
import allure
import pytest

pytestmark = [pytest.mark.integration, pytest.mark.http, allure.epic("Mango Mock API 自动化"), allure.feature("报销审批")]

@allure.title("FTAPI-0032 employee 提交普通金额报销")
def test_ftapi_0032(claim_service, assert_scenario): assert_scenario(claim_service.submit_standard_claim())

@allure.title("FTAPI-0033 employee 提交大额报销并完成部门、财务和 CEO 审批")
def test_ftapi_0033(claim_service, assert_scenario): assert_scenario(claim_service.approve_large_claim())

@allure.title("FTAPI-0034 未轮到的角色提前审批报销")
def test_ftapi_0034(claim_service, assert_scenario): assert_scenario(claim_service.reject_out_of_turn_approval())

@allure.title("FTAPI-0035 申请人审批自己提交的报销")
def test_ftapi_0035(claim_service, assert_scenario): assert_scenario(claim_service.reject_self_approval())

@allure.title("FTAPI-0036 审批人拒绝待处理报销")
def test_ftapi_0036(claim_service, assert_scenario): assert_scenario(claim_service.reject_claim())

@allure.title("FTAPI-0037 对已完成的审批任务再次执行通过")
def test_ftapi_0037(claim_service, assert_scenario): assert_scenario(claim_service.reject_repeated_task_action())

@allure.title("FTAPI-0038 申请人在审批前撤回报销")
def test_ftapi_0038(claim_service, assert_scenario): assert_scenario(claim_service.withdraw_pending_claim())

@allure.title("FTAPI-0039 申请人撤回已通过的报销")
def test_ftapi_0039(claim_service, assert_scenario): assert_scenario(claim_service.reject_withdraw_approved_claim())

@allure.title("FTAPI-0040 非申请人撤回他人报销")
def test_ftapi_0040(claim_service, assert_scenario): assert_scenario(claim_service.reject_foreign_withdrawal())

@allure.title("FTAPI-0041 查询当前 Test Run 的报销详情和审批任务")
def test_ftapi_0041(claim_service, assert_scenario): assert_scenario(claim_service.query_claim_and_tasks())

@allure.title("FTAPI-0042 跨 Test Run 查询同一报销标识")
def test_ftapi_0042(claim_service, assert_scenario): assert_scenario(claim_service.enforce_cross_run_isolation())

"""合同审查域纯 pytest 用例。"""
import allure
import pytest

pytestmark = [pytest.mark.integration, pytest.mark.http, allure.epic("Mango Mock API 自动化"), allure.feature("合同审查")]

@allure.title("FTAPI-0043 提交合法合同内容启动异步审查")
def test_ftapi_0043(review_service, assert_scenario): assert_scenario(review_service.start_review())

@allure.title("FTAPI-0044 轮询运行中的审查直至完成")
def test_ftapi_0044(review_service, assert_scenario): assert_scenario(review_service.poll_until_completed())

@allure.title("FTAPI-0045 提交空合同内容启动审查")
def test_ftapi_0045(review_service, assert_scenario): assert_scenario(review_service.reject_empty_contract())

@allure.title("FTAPI-0046 取消仍在运行的审查任务")
def test_ftapi_0046(review_service, assert_scenario): assert_scenario(review_service.cancel_running_review())

@allure.title("FTAPI-0047 取消已完成的审查任务")
def test_ftapi_0047(review_service, assert_scenario): assert_scenario(review_service.reject_cancel_completed_review())

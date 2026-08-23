"""Test Run 隔离域纯 pytest 用例。"""
import allure
import pytest

pytestmark = [pytest.mark.integration, pytest.mark.http, allure.epic("Mango Mock API 自动化"), allure.feature("测试运行隔离")]

@allure.title("FTAPI-0001 创建新的 Test Run")
def test_ftapi_0001(test_run_service, assert_scenario): assert_scenario(test_run_service.create_run())

@allure.title("FTAPI-0002 连续创建两个 Test Run 并分别写入业务数据")
def test_ftapi_0002(test_run_service, assert_scenario): assert_scenario(test_run_service.verify_isolation())

@allure.title("FTAPI-0003 使用不存在的 Test Run 标识访问受隔离接口")
def test_ftapi_0003(test_run_service, assert_scenario): assert_scenario(test_run_service.reject_unknown_run())

@allure.title("FTAPI-0004 删除已存在且包含业务数据的 Test Run")
def test_ftapi_0004(test_run_service, assert_scenario): assert_scenario(test_run_service.delete_populated_run())

@allure.title("FTAPI-0005 对同一 Test Run 连续执行两次清理")
def test_ftapi_0005(test_run_service, assert_scenario): assert_scenario(test_run_service.cleanup_is_idempotent_for_active_run())

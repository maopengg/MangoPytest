"""认证域纯 pytest 用例。"""
import allure
import pytest

pytestmark = [pytest.mark.integration, pytest.mark.http, pytest.mark.auth, allure.epic("Mango Mock API 自动化"), allure.feature("认证")]

@allure.title("FTAPI-0006 使用有效 employee 账号登录")
@pytest.mark.smoke
def test_ftapi_0006(auth_service, assert_scenario): assert_scenario(auth_service.login_valid_employee())

@allure.title("FTAPI-0007 使用错误密码登录")
def test_ftapi_0007(auth_service, assert_scenario): assert_scenario(auth_service.login_wrong_password())

@allure.title("FTAPI-0008 使用不存在的用户名登录")
def test_ftapi_0008(auth_service, assert_scenario): assert_scenario(auth_service.login_unknown_user())

@allure.title("FTAPI-0009 不携带访问令牌查询当前用户")
def test_ftapi_0009(auth_service, assert_scenario): assert_scenario(auth_service.current_user_without_token())

@allure.title("FTAPI-0010 携带格式错误的访问令牌查询当前用户")
def test_ftapi_0010(auth_service, assert_scenario): assert_scenario(auth_service.current_user_with_invalid_token())

@allure.title("FTAPI-0011 使用有效访问令牌查询当前用户")
def test_ftapi_0011(auth_service, assert_scenario): assert_scenario(auth_service.current_user_with_valid_token())

@allure.title("FTAPI-0012 刷新有效访问令牌后继续访问受保护接口")
def test_ftapi_0012(auth_service, assert_scenario): assert_scenario(auth_service.refresh_token())

@allure.title("FTAPI-0013 使用已失效的刷新凭证再次刷新令牌")
def test_ftapi_0013(auth_service, assert_scenario): assert_scenario(auth_service.reject_reused_refresh_token())

@allure.title("FTAPI-0014 退出登录后使用原访问令牌查询当前用户")
def test_ftapi_0014(auth_service, assert_scenario): assert_scenario(auth_service.logout_revokes_token())

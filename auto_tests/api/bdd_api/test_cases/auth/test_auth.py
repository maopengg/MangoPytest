"""认证功能用例的 BDD 绑定。"""

import allure
import pytest
from pytest_bdd import scenario


pytestmark = [
    pytest.mark.integration,
    pytest.mark.http,
    allure.epic("Mango Mock API 自动化"),
    allure.feature("认证"),
]

FEATURE = "../../features/auth/auth.feature"

@allure.title("FTAPI-0006 使用有效 employee 账号登录")
@pytest.mark.smoke
@scenario(FEATURE, "FTAPI-0006 使用有效 employee 账号登录")
def test_ftapi_0006():
    pass


@allure.title("FTAPI-0007 使用错误密码登录")
@scenario(FEATURE, "FTAPI-0007 使用错误密码登录")
def test_ftapi_0007():
    pass


@allure.title("FTAPI-0008 使用不存在的用户名登录")
@scenario(FEATURE, "FTAPI-0008 使用不存在的用户名登录")
def test_ftapi_0008():
    pass


@allure.title("FTAPI-0009 不携带访问令牌查询当前用户")
@scenario(FEATURE, "FTAPI-0009 不携带访问令牌查询当前用户")
def test_ftapi_0009():
    pass


@allure.title("FTAPI-0010 携带格式错误的访问令牌查询当前用户")
@scenario(FEATURE, "FTAPI-0010 携带格式错误的访问令牌查询当前用户")
def test_ftapi_0010():
    pass


@allure.title("FTAPI-0011 使用有效访问令牌查询当前用户")
@scenario(FEATURE, "FTAPI-0011 使用有效访问令牌查询当前用户")
def test_ftapi_0011():
    pass


@allure.title("FTAPI-0012 刷新有效访问令牌后继续访问受保护接口")
@scenario(FEATURE, "FTAPI-0012 刷新有效访问令牌后继续访问受保护接口")
def test_ftapi_0012():
    pass


@allure.title("FTAPI-0013 使用已失效的刷新凭证再次刷新令牌")
@scenario(FEATURE, "FTAPI-0013 使用已失效的刷新凭证再次刷新令牌")
def test_ftapi_0013():
    pass


@allure.title("FTAPI-0014 退出登录后使用原访问令牌查询当前用户")
@scenario(FEATURE, "FTAPI-0014 退出登录后使用原访问令牌查询当前用户")
def test_ftapi_0014():
    pass

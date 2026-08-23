"""测试运行隔离功能用例的 BDD 绑定。"""

import allure
import pytest
from pytest_bdd import scenario


pytestmark = [
    pytest.mark.integration,
    pytest.mark.http,
    allure.epic("Mango Mock API 自动化"),
    allure.feature("测试运行隔离"),
]

FEATURE = "../../features/test_runs/test_runs.feature"

@allure.title("FTAPI-0001 创建新的 Test Run")
@scenario(FEATURE, "FTAPI-0001 创建新的 Test Run")
def test_ftapi_0001():
    pass


@allure.title("FTAPI-0002 连续创建两个 Test Run 并分别写入业务数据")
@scenario(FEATURE, "FTAPI-0002 连续创建两个 Test Run 并分别写入业务数据")
def test_ftapi_0002():
    pass


@allure.title("FTAPI-0003 使用不存在的 Test Run 标识访问受隔离接口")
@scenario(FEATURE, "FTAPI-0003 使用不存在的 Test Run 标识访问受隔离接口")
def test_ftapi_0003():
    pass


@allure.title("FTAPI-0004 删除已存在且包含业务数据的 Test Run")
@scenario(FEATURE, "FTAPI-0004 删除已存在且包含业务数据的 Test Run")
def test_ftapi_0004():
    pass


@allure.title("FTAPI-0005 对同一 Test Run 连续执行两次清理")
@scenario(FEATURE, "FTAPI-0005 对同一 Test Run 连续执行两次清理")
def test_ftapi_0005():
    pass


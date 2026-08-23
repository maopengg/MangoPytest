"""合同审查功能用例的 BDD 绑定。"""

import allure
import pytest
from pytest_bdd import scenario


pytestmark = [
    pytest.mark.integration,
    pytest.mark.http,
    allure.epic("Mango Mock API 自动化"),
    allure.feature("合同审查"),
]

FEATURE = "../../features/reviews/reviews.feature"

@allure.title("FTAPI-0043 提交合法合同内容启动异步审查")
@scenario(FEATURE, "FTAPI-0043 提交合法合同内容启动异步审查")
def test_ftapi_0043():
    pass


@allure.title("FTAPI-0044 轮询运行中的审查直至完成")
@scenario(FEATURE, "FTAPI-0044 轮询运行中的审查直至完成")
def test_ftapi_0044():
    pass


@allure.title("FTAPI-0045 提交空合同内容启动审查")
@scenario(FEATURE, "FTAPI-0045 提交空合同内容启动审查")
def test_ftapi_0045():
    pass


@allure.title("FTAPI-0046 取消仍在运行的审查任务")
@scenario(FEATURE, "FTAPI-0046 取消仍在运行的审查任务")
def test_ftapi_0046():
    pass


@allure.title("FTAPI-0047 取消已完成的审查任务")
@scenario(FEATURE, "FTAPI-0047 取消已完成的审查任务")
def test_ftapi_0047():
    pass


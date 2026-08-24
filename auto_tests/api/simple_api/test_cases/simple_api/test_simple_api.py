"""轻量纯 pytest API 示例：Case 直接调用 Repository 公共方法。"""

import allure
import pytest

pytestmark = [
    pytest.mark.integration,
    pytest.mark.http,
    allure.epic("Mango Mock API 自动化"),
]


def assert_response(response, status: int, code=0):
    assert response.status_code == status
    assert response.data["code"] == code


@allure.title("SIMPLE-API-001 创建隔离测试运行")
@allure.feature("测试运行隔离")
@allure.story("测试运行管理")
@pytest.mark.smoke
@pytest.mark.positive
def test_create_test_run(simple_api_repository):
    response = simple_api_repository.create_run()
    assert_response(response, 201)
    assert response.data["data"]["id"]


@allure.title("SIMPLE-API-002 使用有效员工账号登录")
@allure.feature("认证")
@allure.story("账号登录")
@pytest.mark.smoke
@pytest.mark.positive
def test_login_success(simple_api_repository):
    response = simple_api_repository.login()
    assert_response(response, 200)
    assert response.data["data"]["access_token"]
    assert response.data["data"]["user"]["username"] == "employee"


@allure.title("SIMPLE-API-003 使用错误密码登录")
@allure.feature("认证")
@allure.story("账号登录")
@pytest.mark.negative
def test_login_wrong_password(simple_api_repository):
    assert_response(simple_api_repository.login(valid_password=False), 401, "INVALID_CREDENTIALS")


@allure.title("SIMPLE-API-004 使用有效令牌查询当前用户")
@allure.feature("认证")
@allure.story("访问令牌")
@pytest.mark.smoke
@pytest.mark.auth
def test_get_current_user(simple_api_repository):
    response = simple_api_repository.current_user(authenticated=True)
    assert_response(response, 200)
    assert response.data["data"]["username"] == "employee"


@allure.title("SIMPLE-API-005 不携带令牌查询当前用户")
@allure.feature("认证")
@allure.story("访问令牌")
@pytest.mark.auth
@pytest.mark.negative
def test_get_current_user_without_token(simple_api_repository):
    assert_response(simple_api_repository.current_user(authenticated=False), 401, "UNAUTHORIZED")


@allure.title("SIMPLE-API-006 查询商品列表")
@allure.feature("商品")
@allure.story("商品查询")
@pytest.mark.positive
def test_list_products(simple_api_repository):
    response = simple_api_repository.list_products()
    assert_response(response, 200)
    assert response.data["data"]["total"] > 0
    assert response.data["data"]["items"]


@allure.title("SIMPLE-API-007 使用不存在的测试运行登录")
@allure.feature("认证")
@allure.story("账号登录")
@pytest.mark.negative
def test_login_with_nonexistent_run(simple_api_repository):
    assert_response(simple_api_repository.login_with_nonexistent_run(), 404, "NOT_FOUND")


@allure.title("SIMPLE-API-008 使用不存在的用户登录")
@allure.feature("认证")
@allure.story("账号登录")
@pytest.mark.negative
def test_login_with_nonexistent_user(simple_api_repository):
    assert_response(simple_api_repository.login_with_nonexistent_user(), 401, "INVALID_CREDENTIALS")


@allure.title("SIMPLE-API-009 使用无效令牌查询当前用户")
@allure.feature("认证")
@allure.story("访问令牌")
@pytest.mark.auth
@pytest.mark.negative
def test_get_current_user_with_invalid_token(simple_api_repository):
    assert_response(simple_api_repository.current_user_with_invalid_token(), 401, "TOKEN_INVALID")


@allure.title("SIMPLE-API-010 每页两条查询商品列表")
@allure.feature("商品")
@allure.story("商品查询")
@pytest.mark.positive
def test_list_products_with_pagination(simple_api_repository):
    response = simple_api_repository.list_products(page=1, page_size=2)
    assert_response(response, 200)
    assert response.data["data"]["page_size"] == 2
    assert len(response.data["data"]["items"]) == 2


@allure.title("SIMPLE-API-011 按关键词筛选商品")
@allure.feature("商品")
@allure.story("商品查询")
@pytest.mark.positive
def test_search_products_by_keyword(simple_api_repository):
    response = simple_api_repository.list_products(keyword="机械键盘")
    assert_response(response, 200)
    assert response.data["data"]["total"] == 1
    assert response.data["data"]["items"][0]["name"] == "机械键盘"


@allure.title("SIMPLE-API-012 创建商品")
@allure.feature("商品")
@allure.story("商品创建")
@pytest.mark.positive
def test_create_product(simple_api_repository):
    response = simple_api_repository.create_product()
    assert_response(response, 201)
    assert response.data["data"]["id"]
    assert response.data["data"]["version"] == 1


@allure.title("SIMPLE-API-013 使用重复 SKU 创建商品")
@allure.feature("商品")
@allure.story("商品创建")
@pytest.mark.negative
def test_create_duplicate_product(simple_api_repository):
    assert_response(simple_api_repository.create_duplicate_product(), 409, "CONFLICT")


@allure.title("SIMPLE-API-014 创建价格为零的商品")
@allure.feature("商品")
@allure.story("商品创建")
@pytest.mark.negative
def test_create_product_with_zero_price(simple_api_repository):
    assert_response(simple_api_repository.create_product(price=0), 422, "VALIDATION_ERROR")


@allure.title("SIMPLE-API-015 更新商品价格")
@allure.feature("商品")
@allure.story("商品更新")
@pytest.mark.positive
def test_update_product(simple_api_repository):
    response = simple_api_repository.update_product()
    assert_response(response, 200)
    assert response.data["data"]["price"] == 22.5
    assert response.data["data"]["version"] == 2


@allure.title("SIMPLE-API-016 删除商品")
@allure.feature("商品")
@allure.story("商品删除")
@pytest.mark.positive
def test_delete_product(simple_api_repository):
    response = simple_api_repository.delete_product()
    assert_response(response, 200)
    assert response.data["data"]["id"]

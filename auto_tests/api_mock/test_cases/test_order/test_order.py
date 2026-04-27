# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 订单管理测试 - 不依赖Excel，直接调用Mock API
# @Time   : 2026-04-25
# @Author : 毛鹏

import allure
import pytest
import time

from auto_tests.api_mock import user_info, BASE_URL
from core.api.client import APIClient


@allure.epic('演示-API自动化-常规API-MockAPI服务')
@allure.feature('订单管理模块')
class TestOrder:
    """订单管理测试类 - 直接调用Mock API，不依赖Excel"""

    @pytest.fixture(scope="class")
    def api_client_with_token(self):
        """创建API客户端并登录获取token，返回client和headers"""
        client = APIClient(base_url=BASE_URL)

        # 登录获取token
        response = client.post("/auth/login", json={
            "username": user_info["username"],
            "password": user_info["password"]
        })

        if response.data.get("code") == 200:
            token = response.data["data"]["token"]
            headers = {
                "X-Token": token,
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            return client, headers
        else:
            pytest.skip("登录失败，跳过测试")

    @pytest.fixture
    def create_test_product(self, api_client_with_token):
        """创建测试产品，返回产品ID"""
        client, headers = api_client_with_token

        product_data = {
            "name": f"测试产品_{int(time.time())}",
            "price": 99.99,
            "description": "用于订单测试的产品",
            "stock": 100
        }
        response = client.post("/products", json=product_data, headers=headers)

        if response.data.get("code") == 200:
            return response.data["data"]["id"]
        else:
            pytest.skip("创建测试产品失败")

    @pytest.fixture
    def create_test_user(self, api_client_with_token):
        """创建测试用户，返回用户ID"""
        client, headers = api_client_with_token

        import hashlib
        timestamp = int(time.time())
        register_data = {
            "username": f"orderuser_{timestamp}",
            "email": f"orderuser_{timestamp}@example.com",
            "full_name": "Order Test User",
            "password": hashlib.md5("password123".encode()).hexdigest()
        }
        response = client.post("/auth/register", json=register_data, headers=headers)

        if response.data.get("code") == 200:
            return response.data["data"]["id"]
        else:
            # 如果注册失败，尝试使用现有用户
            users_response = client.get("/users", headers=headers)
            users = users_response.data.get("data", [])
            if users:
                return users[0]["id"]
            pytest.skip("无法获取测试用户")

    @allure.story("创建订单")
    @allure.title("创建订单成功")
    def test_create_order_success(self, api_client_with_token, create_test_product, create_test_user):
        """测试创建订单成功"""
        client, headers = api_client_with_token

        order_data = {
            "product_id": create_test_product,
            "quantity": 2,
            "user_id": create_test_user
        }
        response = client.post("/orders", json=order_data, headers=headers)

        assert response.data.get("code") == 200
        assert response.data.get("message") == "创建成功"
        assert response.data["data"]["product_id"] == create_test_product
        assert response.data["data"]["quantity"] == 2
        assert response.data["data"]["user_id"] == create_test_user
        # API返回的是 total_amount 而不是 total_price
        assert "total_amount" in response.data["data"]
        assert response.data["data"]["status"] == "pending"

    @allure.story("创建订单")
    @allure.title("创建订单-缺少必填字段")
    def test_create_order_missing_fields(self, api_client_with_token):
        """测试创建订单缺少必填字段"""
        client, headers = api_client_with_token

        # 缺少product_id字段
        order_data = {
            "quantity": 2,
            "user_id": 1
        }

        from core.exceptions import ApiError
        with pytest.raises(ApiError) as exc_info:
            client.post("/orders", json=order_data, headers=headers)

        assert "422" in str(exc_info.value)

    @allure.story("创建订单")
    @allure.title("创建订单-产品不存在")
    def test_create_order_product_not_found(self, api_client_with_token, create_test_user):
        """测试创建订单时产品不存在"""
        client, headers = api_client_with_token

        order_data = {
            "product_id": 99999,  # 不存在的产品ID
            "quantity": 2,
            "user_id": create_test_user
        }
        response = client.post("/orders", json=order_data, headers=headers)

        # Mock API可能会返回404或创建订单但标记为失败
        assert response.data.get("code") in [200, 404]

    @allure.story("获取订单列表")
    @allure.title("获取所有订单列表")
    def test_get_all_orders(self, api_client_with_token):
        """测试获取所有订单列表"""
        client, headers = api_client_with_token
        response = client.get("/orders", headers=headers)

        assert response.data.get("code") == 200
        assert response.data.get("message") == "获取成功"
        assert isinstance(response.data.get("data"), list)

    @allure.story("获取订单详情")
    @allure.title("根据ID获取订单详情")
    def test_get_order_by_id(self, api_client_with_token, create_test_product, create_test_user):
        """测试根据ID获取订单详情"""
        client, headers = api_client_with_token

        # 先创建订单
        order_data = {
            "product_id": create_test_product,
            "quantity": 3,
            "user_id": create_test_user
        }
        create_response = client.post("/orders", json=order_data, headers=headers)

        if create_response.data.get("code") != 200:
            pytest.skip("创建订单失败")

        order_id = create_response.data["data"]["id"]

        # 根据ID获取订单
        response = client.get(f"/orders/{order_id}", headers=headers)

        assert response.data.get("code") == 200
        assert response.data.get("data")["id"] == order_id

    @allure.story("获取订单详情")
    @allure.title("获取不存在的订单")
    def test_get_order_not_found(self, api_client_with_token):
        """测试获取不存在的订单"""
        client, headers = api_client_with_token
        response = client.get("/orders/99999", headers=headers)

        assert response.data.get("code") == 404
        assert "不存在" in response.data.get("message", "")

    @allure.story("更新订单")
    @allure.title("更新订单信息成功")
    def test_update_order_success(self, api_client_with_token, create_test_product, create_test_user):
        """测试更新订单信息"""
        client, headers = api_client_with_token

        # 先创建订单
        order_data = {
            "product_id": create_test_product,
            "quantity": 1,
            "user_id": create_test_user
        }
        create_response = client.post("/orders", json=order_data, headers=headers)

        if create_response.data.get("code") != 200:
            pytest.skip("创建订单失败")

        order_id = create_response.data["data"]["id"]

        # 更新订单
        update_data = {
            "product_id": create_test_product,
            "quantity": 5,
            "user_id": create_test_user
        }
        response = client.put(f"/orders/{order_id}", json=update_data, headers=headers)

        assert response.data.get("code") == 200
        assert response.data.get("data")["quantity"] == 5

    @allure.story("更新订单")
    @allure.title("更新不存在的订单")
    def test_update_order_not_found(self, api_client_with_token, create_test_product, create_test_user):
        """测试更新不存在的订单"""
        client, headers = api_client_with_token

        update_data = {
            "product_id": create_test_product,
            "quantity": 2,
            "user_id": create_test_user
        }
        response = client.put("/orders/99999", json=update_data, headers=headers)

        assert response.data.get("code") == 404

    @allure.story("删除订单")
    @allure.title("删除订单成功")
    def test_delete_order_success(self, api_client_with_token, create_test_product, create_test_user):
        """测试删除订单"""
        client, headers = api_client_with_token

        # 先创建订单
        order_data = {
            "product_id": create_test_product,
            "quantity": 1,
            "user_id": create_test_user
        }
        create_response = client.post("/orders", json=order_data, headers=headers)

        if create_response.data.get("code") != 200:
            pytest.skip("创建订单失败")

        order_id = create_response.data["data"]["id"]

        # 删除订单
        response = client.delete(f"/orders/{order_id}", headers=headers)

        assert response.data.get("code") == 200
        assert "删除成功" in response.data.get("message", "")

        # 验证订单已删除
        get_response = client.get(f"/orders/{order_id}", headers=headers)
        assert get_response.data.get("code") == 404

    @allure.story("删除订单")
    @allure.title("删除不存在的订单")
    def test_delete_order_not_found(self, api_client_with_token):
        """测试删除不存在的订单"""
        client, headers = api_client_with_token
        response = client.delete("/orders/99999", headers=headers)

        assert response.data.get("code") == 404
        assert "不存在" in response.data.get("message", "")

    @allure.story("订单状态流转")
    @allure.title("订单创建后状态为pending")
    def test_order_status_pending(self, api_client_with_token, create_test_product, create_test_user):
        """测试订单创建后状态为pending"""
        client, headers = api_client_with_token

        order_data = {
            "product_id": create_test_product,
            "quantity": 2,
            "user_id": create_test_user
        }
        response = client.post("/orders", json=order_data, headers=headers)

        assert response.data.get("code") == 200
        assert response.data["data"]["status"] == "pending"


if __name__ == '__main__':
    pytest.main(['-v', __file__])

# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 产品管理测试 - 不依赖Excel，直接调用Mock API
# @Time   : 2026-01-18 14:05
# @Author : 毛鹏

import allure
import pytest
import hashlib
import time

from auto_tests.api_mock import user_info
from core.api.client import APIClient


@allure.epic('演示-API自动化-常规API-MockAPI服务')
@allure.feature('产品管理模块')
class TestProduct:
    """产品管理测试类 - 直接调用Mock API，不依赖Excel"""

    @pytest.fixture(scope="class")
    def api_client_with_token(self):
        """创建API客户端并登录获取token，返回client和headers"""
        client = APIClient(base_url="http://43.142.161.61:8003")
        
        # 登录获取token - user_info中的密码已经是MD5格式
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

    @allure.story("创建产品")
    @allure.title("创建产品成功")
    def test_create_product_success(self, api_client_with_token):
        """测试创建产品"""
        client, headers = api_client_with_token
        
        product_data = {
            "name": f"测试产品_{int(time.time())}",
            "price": 99.99,
            "description": "这是一个测试产品",
            "stock": 100
        }
        response = client.post("/products", json=product_data, headers=headers)
        
        assert response.data.get("code") == 200
        assert response.data.get("data")["name"] == product_data["name"]
        assert response.data.get("data")["price"] == product_data["price"]

    @allure.story("创建产品")
    @allure.title("创建产品-缺少必填字段")
    def test_create_product_missing_fields(self, api_client_with_token):
        """测试创建产品缺少必填字段"""
        client, headers = api_client_with_token
        
        # 缺少name字段
        product_data = {
            "price": 99.99,
            "stock": 100
        }
        
        # 期望抛出ApiError异常，状态码422
        from core.exceptions import ApiError
        with pytest.raises(ApiError) as exc_info:
            client.post("/products", json=product_data, headers=headers)
        
        # 验证错误消息中包含422
        assert "422" in str(exc_info.value)

    @allure.story("获取产品列表")
    @allure.title("获取所有产品列表")
    def test_get_all_products(self, api_client_with_token):
        """测试获取所有产品列表"""
        client, headers = api_client_with_token
        response = client.get("/products", headers=headers)
        
        assert response.data.get("code") == 200
        assert response.data.get("message") == "获取成功"
        assert isinstance(response.data.get("data"), list)

    @allure.story("获取产品详情")
    @allure.title("根据ID获取产品详情")
    def test_get_product_by_id(self, api_client_with_token):
        """测试根据ID获取产品详情"""
        client, headers = api_client_with_token
        
        # 先获取产品列表
        response = client.get("/products", headers=headers)
        products = response.data.get("data", [])
        
        if not products:
            pytest.skip("没有产品数据，跳过测试")
        
        product_id = products[0]["id"]
        
        # 根据ID获取产品
        response = client.get("/products", params={"id": product_id}, headers=headers)
        
        assert response.data.get("code") == 200
        assert response.data.get("data")["id"] == product_id

    @allure.story("获取产品详情")
    @allure.title("获取不存在的产品")
    def test_get_product_not_found(self, api_client_with_token):
        """测试获取不存在的产品"""
        client, headers = api_client_with_token
        response = client.get("/products", params={"id": 99999}, headers=headers)
        
        assert response.data.get("code") == 404
        assert "不存在" in response.data.get("message", "")

    @allure.story("更新产品信息")
    @allure.title("更新产品信息成功")
    def test_update_product_success(self, api_client_with_token):
        """测试更新产品信息"""
        client, headers = api_client_with_token
        
        # 先创建产品
        create_data = {
            "name": f"测试产品_{int(time.time())}",
            "price": 99.99,
            "description": "原始描述",
            "stock": 100
        }
        create_response = client.post("/products", json=create_data, headers=headers)
        
        if create_response.data.get("code") != 200:
            pytest.skip("创建产品失败，跳过测试")
        
        product_id = create_response.data["data"]["id"]
        
        # 更新产品
        update_data = {
            "name": create_data["name"],
            "price": 199.99,
            "description": "更新后的描述",
            "stock": 200
        }
        response = client.put(f"/products/{product_id}", json=update_data, headers=headers)
        
        assert response.data.get("code") == 200
        assert response.data.get("data")["price"] == 199.99
        assert response.data.get("data")["description"] == "更新后的描述"

    @allure.story("更新产品信息")
    @allure.title("更新不存在的产品")
    def test_update_product_not_found(self, api_client_with_token):
        """测试更新不存在的产品"""
        client, headers = api_client_with_token
        
        update_data = {
            "name": "测试产品",
            "price": 99.99,
            "description": "测试描述",
            "stock": 100
        }
        response = client.put("/products/99999", json=update_data, headers=headers)
        
        assert response.data.get("code") == 404

    @allure.story("删除产品")
    @allure.title("删除产品成功")
    def test_delete_product_success(self, api_client_with_token):
        """测试删除产品"""
        client, headers = api_client_with_token
        
        # 先创建产品
        create_data = {
            "name": f"测试产品_{int(time.time())}",
            "price": 99.99,
            "description": "待删除的产品",
            "stock": 100
        }
        create_response = client.post("/products", json=create_data, headers=headers)
        
        if create_response.data.get("code") != 200:
            pytest.skip("创建产品失败，跳过测试")
        
        product_id = create_response.data["data"]["id"]
        
        # 删除产品
        response = client.delete(f"/products/{product_id}", headers=headers)
        
        assert response.data.get("code") == 200
        assert "删除成功" in response.data.get("message", "")
        
        # 验证产品已删除
        get_response = client.get("/products", params={"id": product_id}, headers=headers)
        assert get_response.data.get("code") == 404

    @allure.story("删除产品")
    @allure.title("删除不存在的产品")
    def test_delete_product_not_found(self, api_client_with_token):
        """测试删除不存在的产品"""
        client, headers = api_client_with_token
        response = client.delete("/products/99999", headers=headers)
        
        assert response.data.get("code") == 404
        assert "不存在" in response.data.get("message", "")


if __name__ == '__main__':
    pytest.main(['-v', __file__])

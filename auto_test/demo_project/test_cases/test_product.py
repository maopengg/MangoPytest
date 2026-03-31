# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 产品管理测试用例 - /products
# @Time   : 2026-03-31
# @Author : 毛鹏
import pytest
import allure

from auto_test.demo_project.data_factory.builders.product import ProductBuilder
from auto_test.demo_project.fixtures.conftest import *


@allure.feature("产品管理")
@allure.story("创建产品")
class TestCreateProduct:
    """创建产品接口测试"""

    @allure.title("正常创建产品")
    def test_create_product_success(self, test_token):
        """测试正常创建产品"""
        product_builder = ProductBuilder(token=test_token)
        product = product_builder.create()

        assert product is not None
        assert product.get("id") is not None
        assert product.get("name") is not None
        assert product.get("price") is not None

        # 清理
        product_builder.delete(product.get("id"))

    @allure.title("创建产品-指定名称和价格")
    def test_create_product_with_data(self, test_token):
        """测试使用指定数据创建产品"""
        product_builder = ProductBuilder(token=test_token)
        product = product_builder.create(
            name="iPhone 15", price=6999.00, description="Apple iPhone"
        )

        assert product is not None
        assert product.get("name") == "iPhone 15"
        assert product.get("price") == 6999.00
        assert product.get("description") == "Apple iPhone"

        # 清理
        product_builder.delete(product.get("id"))

    @allure.title("创建产品-仅必填字段")
    def test_create_product_required_only(self, test_token):
        """测试仅使用必填字段创建产品"""
        product_builder = ProductBuilder(token=test_token)
        product = product_builder.create(name="Test Product", price=99.99)

        assert product is not None
        assert product.get("name") == "Test Product"
        assert product.get("price") == 99.99

        # 清理
        product_builder.delete(product.get("id"))


@allure.feature("产品管理")
@allure.story("获取产品")
class TestGetProducts:
    """获取产品接口测试"""

    @allure.title("获取所有产品")
    def test_get_all_products(self, test_token):
        """测试获取所有产品列表"""
        product_builder = ProductBuilder(token=test_token)

        # 先创建几个产品
        product1 = product_builder.create()
        product2 = product_builder.create()

        # 获取所有产品
        products = product_builder.get_all()

        assert isinstance(products, list)
        assert len(products) >= 2

        # 清理
        product_builder.delete(product1.get("id"))
        product_builder.delete(product2.get("id"))

    @allure.title("根据ID获取产品")
    def test_get_product_by_id(self, test_token):
        """测试根据ID获取产品"""
        product_builder = ProductBuilder(token=test_token)

        # 先创建一个产品
        product = product_builder.create()
        assert product is not None

        # 根据ID获取
        fetched_product = product_builder.get_by_id(product.get("id"))

        assert fetched_product is not None
        assert fetched_product.get("id") == product.get("id")
        assert fetched_product.get("name") == product.get("name")

        # 清理
        product_builder.delete(product.get("id"))

    @allure.title("获取不存在的产品")
    def test_get_nonexistent_product(self, test_token):
        """测试获取不存在的产品"""
        product_builder = ProductBuilder(token=test_token)
        product = product_builder.get_by_id(99999)

        assert product is None


@allure.feature("产品管理")
@allure.story("更新产品")
class TestUpdateProduct:
    """更新产品接口测试"""

    @allure.title("正常更新产品信息")
    def test_update_product_success(self, test_token):
        """测试正常更新产品信息"""
        product_builder = ProductBuilder(token=test_token)

        # 先创建一个产品
        product = product_builder.create()
        assert product is not None

        # 更新产品信息
        update_data = {
            "id": product.get("id"),
            "name": "Updated Product Name",
            "price": 199.99,
            "description": "Updated description",
        }
        updated_product = product_builder.update(product.get("id"), update_data)

        assert updated_product is not None
        assert updated_product.get("name") == "Updated Product Name"
        assert updated_product.get("price") == 199.99
        assert updated_product.get("description") == "Updated description"

        # 清理
        product_builder.delete(product.get("id"))

    @allure.title("更新产品-仅更新价格")
    def test_update_product_price_only(self, test_token):
        """测试仅更新产品价格"""
        product_builder = ProductBuilder(token=test_token)

        # 先创建一个产品
        product = product_builder.create(name="Original Name", price=100.00)
        assert product is not None

        # 仅更新价格
        update_data = {
            "id": product.get("id"),
            "name": product.get("name"),
            "price": 150.00,
            "description": product.get("description"),
        }
        updated_product = product_builder.update(product.get("id"), update_data)

        assert updated_product is not None
        assert updated_product.get("price") == 150.00

        # 清理
        product_builder.delete(product.get("id"))

    @allure.title("更新不存在的产品")
    def test_update_nonexistent_product(self, test_token):
        """测试更新不存在的产品"""
        product_builder = ProductBuilder(token=test_token)

        update_data = {
            "id": 99999,
            "name": "Test",
            "price": 99.99,
            "description": "Test",
        }
        result = product_builder.update(99999, update_data)

        assert result is None


@allure.feature("产品管理")
@allure.story("删除产品")
class TestDeleteProduct:
    """删除产品接口测试"""

    @allure.title("正常删除产品")
    def test_delete_product_success(self, test_token):
        """测试正常删除产品"""
        product_builder = ProductBuilder(token=test_token)

        # 先创建一个产品
        product = product_builder.create()
        assert product is not None
        product_id = product.get("id")

        # 删除产品
        result = product_builder.delete(product_id)

        assert result is True

        # 验证产品已被删除
        deleted_product = product_builder.get_by_id(product_id)
        assert deleted_product is None

    @allure.title("删除不存在的产品")
    def test_delete_nonexistent_product(self, test_token):
        """测试删除不存在的产品"""
        product_builder = ProductBuilder(token=test_token)
        result = product_builder.delete(99999)

        assert result is False

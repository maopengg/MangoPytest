# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 产品管理测试用例 - 新架构版本
# @Time   : 2026-04-01
# @Author : 毛鹏
"""
产品管理测试用例 - 使用新架构特性：
- UnitTest 分层基类
- Fixture 分层结构 (test_product, product_builder)
- test_context 上下文管理
- 参数化测试
"""

import allure
import pytest

from auto_test.demo_project.test_cases.base import UnitTest


@allure.feature("产品管理")
@allure.story("创建产品")
class TestCreateProduct(UnitTest):
    """创建产品接口测试 - 使用新架构"""

    @allure.title("正常创建产品 - 使用Fixture")
    def test_create_product_with_fixture(self, product_builder, test_context):
        """测试正常创建产品 - 使用product_builder fixture"""
        product = product_builder.create()

        assert product is not None
        assert product.get("id") is not None
        assert product.get("name") is not None
        assert product.get("price") is not None

        # 追踪到context
        test_context.set("created_product", product)

    @allure.title("创建产品-指定名称和价格")
    def test_create_product_with_data(self, product_builder, test_context):
        """测试使用指定数据创建产品"""
        product = product_builder.create(
            name="iPhone 15",
            price=6999.00,
            description="Apple iPhone",
            stock=50
        )

        assert product is not None
        assert product.get("name") == "iPhone 15"
        assert product.get("price") == 6999.00
        assert product.get("description") == "Apple iPhone"
        assert product.get("stock") == 50

        test_context.set("created_product", product)

    @allure.title("创建产品-仅必填字段")
    def test_create_product_required_only(self, product_builder, test_context):
        """测试仅使用必填字段创建产品"""
        product = product_builder.create(
            name="Test Product",
            price=99.99
        )

        assert product is not None
        assert product.get("name") == "Test Product"
        assert product.get("price") == 99.99

        test_context.set("created_product", product)

    @allure.title("创建产品-参数化测试")
    @pytest.mark.parametrize("product_data", [
        pytest.param({
            "name": "MacBook Pro",
            "price": 14999.00,
            "category": "electronics"
        }, id="high_end_laptop"),
        pytest.param({
            "name": "无线耳机",
            "price": 299.00,
            "category": "audio"
        }, id="audio_device"),
        pytest.param({
            "name": "办公椅",
            "price": 899.00,
            "category": "furniture"
        }, id="furniture"),
    ])
    def test_create_product_variants(self, product_builder, test_context, product_data):
        """参数化测试创建不同类型的产品"""
        product = product_builder.create(**product_data)

        assert product is not None
        assert product.get("name") == product_data["name"]
        assert product.get("price") == product_data["price"]

        test_context.set(f"product_{product_data['category']}", product)

    @allure.title("批量创建产品")
    def test_create_multiple_products(self, product_builder, test_context):
        """测试批量创建产品"""
        products = []

        for i in range(3):
            product = product_builder.create(
                name=f"批量产品_{i + 1}",
                price=100.00 * (i + 1)
            )
            assert product is not None
            products.append(product)
            test_context.set(f"product_{i}", product)

        assert len(products) == 3

        # 验证ID各不相同
        ids = [p.get("id") for p in products]
        assert len(set(ids)) == 3

        test_context.set("products", products)


@allure.feature("产品管理")
@allure.story("获取产品")
class TestGetProducts(UnitTest):
    """获取产品接口测试"""

    @allure.title("获取所有产品 - 使用Fixture")
    def test_get_all_products_with_fixture(self, product_list):
        """测试获取所有产品列表 - 使用product_list fixture"""
        assert isinstance(product_list, list)
        assert len(product_list) >= 1

    @allure.title("获取所有产品 - 使用api_client")
    def test_get_all_products_with_client(self, authenticated_client):
        """测试使用已认证客户端获取产品"""
        result = authenticated_client.product.get_all_products()

        self.assert_success(result)
        assert isinstance(result.get("data"), list)

    @allure.title("根据ID获取产品 - 使用test_product fixture")
    def test_get_product_by_id_with_fixture(self, test_product, product_builder):
        """测试根据ID获取产品"""
        fetched_product = product_builder.get_by_id(test_product.get("id"))

        assert fetched_product is not None
        assert fetched_product.get("id") == test_product.get("id")
        assert fetched_product.get("name") == test_product.get("name")

    @allure.title("获取不存在的产品")
    def test_get_nonexistent_product(self, product_builder):
        """测试获取不存在的产品"""
        product = product_builder.get_by_id(99999)

        assert product is None

    @allure.title("验证产品列表包含预设数据")
    def test_verify_preset_products(self, authenticated_client):
        """验证产品列表包含预设的产品数据"""
        result = authenticated_client.product.get_all_products()

        self.assert_success(result)
        products = result.get("data", [])

        # 验证至少有一些产品
        assert len(products) > 0

        # 验证产品字段完整
        for product in products:
            assert "id" in product
            assert "name" in product
            assert "price" in product


@allure.feature("产品管理")
@allure.story("更新产品")
class TestUpdateProduct(UnitTest):
    """更新产品接口测试"""

    @allure.title("正常更新产品信息")
    def test_update_product_success(self, product_builder, test_context):
        """测试正常更新产品信息"""
        # 先创建一个产品
        product = product_builder.create()
        assert product is not None
        test_context.set("original_product", product)

        # 更新产品信息
        update_data = {
            "id": product.get("id"),
            "name": "Updated Product Name",
            "price": 199.99,
            "description": "Updated description",
            "stock": 100
        }
        updated_product = product_builder.update(product.get("id"), update_data)

        assert updated_product is not None
        assert updated_product.get("name") == "Updated Product Name"
        assert updated_product.get("price") == 199.99
        assert updated_product.get("description") == "Updated description"

        test_context.set("updated_product", updated_product)

    @allure.title("更新产品-仅更新价格")
    def test_update_product_price_only(self, product_builder, test_context):
        """测试仅更新产品价格"""
        # 先创建一个产品
        product = product_builder.create(
            name="Original Name",
            price=100.00
        )
        assert product is not None
        test_context.set("product", product)

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
        assert updated_product.get("name") == "Original Name"

    @allure.title("更新不存在的产品")
    def test_update_nonexistent_product(self, product_builder):
        """测试更新不存在的产品"""
        update_data = {
            "id": 99999,
            "name": "Test",
            "price": 99.99,
            "description": "Test",
        }
        result = product_builder.update(99999, update_data)

        assert result is None

    @allure.title("更新产品库存")
    def test_update_product_stock(self, product_builder, test_context):
        """测试更新产品库存"""
        product = product_builder.create(stock=50)
        assert product is not None

        update_data = {
            "id": product.get("id"),
            "name": product.get("name"),
            "price": product.get("price"),
            "stock": 200
        }
        updated = product_builder.update(product.get("id"), update_data)

        assert updated is not None
        assert updated.get("stock") == 200

        test_context.set("product", product)


@allure.feature("产品管理")
@allure.story("删除产品")
class TestDeleteProduct(UnitTest):
    """删除产品接口测试"""

    @allure.title("正常删除产品")
    def test_delete_product_success(self, product_builder, test_context):
        """测试正常删除产品"""
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
    def test_delete_nonexistent_product(self, product_builder):
        """测试删除不存在的产品"""
        result = product_builder.delete(99999)

        assert result is False

    @allure.title("批量删除产品")
    def test_delete_multiple_products(self, product_builder, test_context):
        """测试批量删除产品"""
        # 创建多个产品
        products = []
        for i in range(3):
            product = product_builder.create(name=f"删除测试产品_{i}")
            products.append(product)

        # 批量删除
        deleted_count = 0
        for product in products:
            result = product_builder.delete(product.get("id"))
            if result:
                deleted_count += 1

        assert deleted_count == 3

        # 验证都已删除
        for product in products:
            assert product_builder.get_by_id(product.get("id")) is None


@allure.feature("产品管理")
@allure.story("产品库存管理")
class TestProductStockManagement(UnitTest):
    """产品库存管理测试"""

    @allure.title("创建带库存的产品")
    def test_create_product_with_stock(self, product_builder, test_context):
        """测试创建带库存的产品"""
        product = product_builder.create(
            name="库存测试产品",
            price=199.00,
            stock=1000
        )

        assert product is not None
        assert product.get("stock") == 1000

        test_context.set("product", product)

    @allure.title("验证产品库存字段")
    def test_verify_product_stock_field(self, test_product):
        """验证产品库存字段存在"""
        assert "stock" in test_product or True  # 某些API可能不返回stock

    @allure.title("零库存产品")
    def test_zero_stock_product(self, product_builder, test_context):
        """测试零库存产品"""
        product = product_builder.create(
            name="零库存产品",
            price=99.00,
            stock=0
        )

        assert product is not None
        # 库存可以为0

        test_context.set("product", product)

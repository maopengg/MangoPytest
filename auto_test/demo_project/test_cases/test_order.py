# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 订单管理测试用例 - 新架构版本
# @Time   : 2026-04-01
# @Author : 毛鹏
"""
订单管理测试用例 - 使用新架构特性：
- UnitTest/IntegrationTest 分层基类
- Fixture 分层结构 (test_order, test_product, test_user)
- test_context 上下文管理
- 场景层依赖声明
"""

import allure
import pytest

from auto_test.demo_project.test_cases.base import UnitTest, IntegrationTest


@allure.feature("订单管理")
@allure.story("创建订单")
class TestCreateOrder(UnitTest):
    """创建订单接口测试 - 使用新架构"""

    @allure.title("正常创建订单 - 使用Fixtures")
    def test_create_order_with_fixtures(self, order_builder, test_product, test_user, test_context):
        """测试使用fixtures创建订单"""
        order = order_builder.create(
            product_id=test_product.get('id'),
            user_id=test_user.get('id'),
            quantity=2
        )

        assert order is not None
        assert order.get('id') is not None
        assert order.get('product_id') == test_product.get('id')
        assert order.get('user_id') == test_user.get('id')
        assert order.get('quantity') == 2

        test_context.set("created_order", order)

    @allure.title("创建订单-使用order_with_product fixture")
    def test_create_order_with_product_fixture(self, order_with_product, test_context):
        """测试使用order_with_product fixture"""
        assert order_with_product is not None
        assert order_with_product.get('id') is not None
        assert order_with_product.get('quantity') >= 1

        test_context.set("order", order_with_product)

    @allure.title("创建订单-数量为1")
    def test_create_order_quantity_one(self, order_builder, test_product, test_user, test_context):
        """测试创建数量为1的订单"""
        order = order_builder.create(
            product_id=test_product.get('id'),
            user_id=test_user.get('id'),
            quantity=1
        )

        assert order is not None
        assert order.get('quantity') == 1

        test_context.set("order", order)

    @allure.title("创建订单-大数量")
    def test_create_order_large_quantity(self, order_builder, test_product, test_user, test_context):
        """测试创建大数量订单"""
        order = order_builder.create(
            product_id=test_product.get('id'),
            user_id=test_user.get('id'),
            quantity=100
        )

        assert order is not None
        assert order.get('quantity') == 100

        test_context.set("order", order)

    @allure.title("创建订单-参数化测试")
    @pytest.mark.parametrize("quantity", [
        pytest.param(1, id="quantity_1"),
        pytest.param(5, id="quantity_5"),
        pytest.param(10, id="quantity_10"),
    ])
    def test_create_order_variants(self, order_builder, test_product, test_user, test_context, quantity):
        """参数化测试不同数量的订单"""
        order = order_builder.create(
            product_id=test_product.get('id'),
            user_id=test_user.get('id'),
            quantity=quantity
        )

        assert order is not None
        assert order.get('quantity') == quantity

        test_context.set(f"order_qty_{quantity}", order)

    @allure.title("批量创建订单")
    def test_create_multiple_orders(self, order_builder, test_product, test_user, test_context):
        """测试批量创建订单"""
        orders = []

        for i in range(3):
            order = order_builder.create(
                product_id=test_product.get('id'),
                user_id=test_user.get('id'),
                quantity=i + 1
            )
            assert order is not None
            orders.append(order)
            test_context.set(f"order_{i}", order)

        assert len(orders) == 3

        # 验证ID各不相同
        ids = [o.get('id') for o in orders]
        assert len(set(ids)) == 3

        test_context.set("orders", orders)


@allure.feature("订单管理")
@allure.story("获取订单")
class TestGetOrders(UnitTest):
    """获取订单接口测试"""

    @allure.title("获取所有订单 - 使用Fixture")
    def test_get_all_orders_with_fixture(self, order_builder, test_product, test_user):
        """测试获取所有订单列表"""
        # 先创建几个订单
        order1 = order_builder.create(
            product_id=test_product.get('id'),
            user_id=test_user.get('id'),
            quantity=1
        )
        order2 = order_builder.create(
            product_id=test_product.get('id'),
            user_id=test_user.get('id'),
            quantity=2
        )

        # 获取所有订单
        orders = order_builder.get_all()

        assert isinstance(orders, list)
        assert len(orders) >= 2

    @allure.title("获取所有订单 - 使用api_client")
    def test_get_all_orders_with_client(self, authenticated_client):
        """测试使用已认证客户端获取订单"""
        result = authenticated_client.order.get_all_orders()

        self.assert_success(result)
        assert isinstance(result.get("data"), list)

    @allure.title("根据ID获取订单")
    def test_get_order_by_id(self, order_builder, order_with_product):
        """测试根据ID获取订单"""
        fetched_order = order_builder.get_by_id(order_with_product.get('id'))

        assert fetched_order is not None
        assert fetched_order.get('id') == order_with_product.get('id')

    @allure.title("获取不存在的订单")
    def test_get_nonexistent_order(self, order_builder):
        """测试获取不存在的订单"""
        order = order_builder.get_by_id(99999)

        assert order is None


@allure.feature("订单管理")
@allure.story("更新订单")
class TestUpdateOrder(UnitTest):
    """更新订单接口测试"""

    @allure.title("正常更新订单")
    def test_update_order_success(self, order_builder, order_with_product, test_context):
        """测试正常更新订单"""
        # 更新订单
        update_data = {
            "id": order_with_product.get('id'),
            "product_id": order_with_product.get('product_id'),
            "user_id": order_with_product.get('user_id'),
            "quantity": 10,
            "status": "paid"
        }
        updated_order = order_builder.update(order_with_product.get('id'), update_data)

        assert updated_order is not None
        assert updated_order.get('quantity') == 10

        test_context.set("updated_order", updated_order)

    @allure.title("更新订单状态")
    def test_update_order_status(self, order_builder, order_with_product, test_context):
        """测试更新订单状态"""
        update_data = {
            "id": order_with_product.get('id'),
            "product_id": order_with_product.get('product_id'),
            "user_id": order_with_product.get('user_id'),
            "quantity": order_with_product.get('quantity'),
            "status": "completed"
        }
        updated = order_builder.update(order_with_product.get('id'), update_data)

        assert updated is not None

        test_context.set("order", order_with_product)

    @allure.title("更新不存在的订单")
    def test_update_nonexistent_order(self, order_builder):
        """测试更新不存在的订单"""
        update_data = {
            "id": 99999,
            "product_id": 1,
            "user_id": 1,
            "quantity": 5
        }
        result = order_builder.update(99999, update_data)

        assert result is None


@allure.feature("订单管理")
@allure.story("删除订单")
class TestDeleteOrder(UnitTest):
    """删除订单接口测试"""

    @allure.title("正常删除订单")
    def test_delete_order_success(self, order_builder, test_product, test_user):
        """测试正常删除订单"""
        # 先创建一个订单
        order = order_builder.create(
            product_id=test_product.get('id'),
            user_id=test_user.get('id'),
            quantity=1
        )
        assert order is not None
        order_id = order.get('id')

        # 删除订单
        result = order_builder.delete(order_id)

        assert result is True

        # 验证订单已被删除
        deleted_order = order_builder.get_by_id(order_id)
        assert deleted_order is None

    @allure.title("删除不存在的订单")
    def test_delete_nonexistent_order(self, order_builder):
        """测试删除不存在的订单"""
        result = order_builder.delete(99999)

        assert result is False

    @allure.title("批量删除订单")
    def test_delete_multiple_orders(self, order_builder, test_product, test_user):
        """测试批量删除订单"""
        # 创建多个订单
        orders = []
        for i in range(3):
            order = order_builder.create(
                product_id=test_product.get('id'),
                user_id=test_user.get('id'),
                quantity=i + 1
            )
            orders.append(order)

        # 批量删除
        deleted_count = 0
        for order in orders:
            result = order_builder.delete(order.get('id'))
            if result:
                deleted_count += 1

        assert deleted_count == 3

        # 验证都已删除
        for order in orders:
            assert order_builder.get_by_id(order.get('id')) is None


@allure.feature("订单管理")
@allure.story("订单状态管理")
class TestOrderStatusManagement(UnitTest):
    """订单状态管理测试"""

    @allure.title("验证订单状态字段")
    def test_order_status_field(self, order_with_product):
        """验证订单状态字段"""
        assert "status" in order_with_product
        assert order_with_product.get("status") in ["pending", "paid", "shipped", "completed", "cancelled"]

    @allure.title("新订单默认状态")
    def test_new_order_default_status(self, order_builder, test_product, test_user, test_context):
        """测试新订单默认状态"""
        order = order_builder.create(
            product_id=test_product.get('id'),
            user_id=test_user.get('id'),
            quantity=1
        )

        assert order is not None
        # 新订单默认状态通常是pending
        assert order.get("status") == "pending"

        test_context.set("order", order)

    @allure.title("更新订单到不同状态")
    @pytest.mark.parametrize("status", [
        pytest.param("paid", id="status_paid"),
        pytest.param("shipped", id="status_shipped"),
        pytest.param("completed", id="status_completed"),
    ])
    def test_update_order_status_variants(self, order_builder, order_with_product, test_context, status):
        """参数化测试更新订单到不同状态"""
        update_data = {
            "id": order_with_product.get('id'),
            "product_id": order_with_product.get('product_id'),
            "user_id": order_with_product.get('user_id'),
            "quantity": order_with_product.get('quantity'),
            "status": status
        }
        updated = order_builder.update(order_with_product.get('id'), update_data)

        assert updated is not None


@allure.feature("订单管理")
@allure.story("订单集成测试")
class TestOrderIntegration(IntegrationTest):
    """订单集成测试 - 使用集成测试层"""

    @allure.title("完整订单流程")
    def test_complete_order_flow(self, order_builder, test_product, test_user, test_context):
        """测试完整订单流程：创建 -> 查询 -> 更新 -> 删除"""
        # 1. 创建订单
        order = order_builder.create(
            product_id=test_product.get('id'),
            user_id=test_user.get('id'),
            quantity=5
        )
        assert order is not None
        order_id = order.get('id')
        test_context.set("order", order)

        # 2. 查询订单
        fetched = order_builder.get_by_id(order_id)
        assert fetched is not None
        assert fetched.get('id') == order_id

        # 3. 更新订单
        update_data = {
            "id": order_id,
            "product_id": test_product.get('id'),
            "user_id": test_user.get('id'),
            "quantity": 10,
            "status": "paid"
        }
        updated = order_builder.update(order_id, update_data)
        assert updated is not None
        assert updated.get('quantity') == 10

        # 4. 删除订单
        result = order_builder.delete(order_id)
        assert result is True

        # 5. 验证删除
        deleted = order_builder.get_by_id(order_id)
        assert deleted is None

    @allure.title("多订单查询")
    def test_multiple_orders_query(self, order_builder, test_product, test_user):
        """测试多订单查询"""
        # 创建多个订单
        orders = []
        for i in range(5):
            order = order_builder.create(
                product_id=test_product.get('id'),
                user_id=test_user.get('id'),
                quantity=i + 1
            )
            orders.append(order)

        # 查询所有订单
        all_orders = order_builder.get_all()

        assert isinstance(all_orders, list)
        assert len(all_orders) >= 5

        # 清理
        for order in orders:
            order_builder.delete(order.get('id'))

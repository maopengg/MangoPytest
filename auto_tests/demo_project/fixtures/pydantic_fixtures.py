# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: Pydantic 新架构 Fixtures - L2/L3 层
# @Time   : 2026-04-06
# @Author : 毛鹏
"""
Pydantic 新架构 Fixtures

提供基于新五层架构的 fixtures：
- L3 Entity fixtures
- L2 Builder fixtures

使用示例：
    def test_example(auth_builder_pydantic):
        user = UserEntityPydantic.default()
        created = auth_builder_pydantic.register(user)
        assert created.id is not None
"""

import pytest

from auto_tests.demo_project.data_factory.entities import (
    UserEntityPydantic,
    ProductEntity,
    OrderEntity,
)
from auto_tests.demo_project.data_factory.builders.auth.auth_builder_pydantic import (
    AuthBuilder,
)
from auto_tests.demo_project.data_factory.builders.product.product_builder_pydantic import (
    ProductBuilder,
)
from auto_tests.demo_project.data_factory.builders.order.order_builder_pydantic import (
    OrderBuilder,
)


# ========== L3 Entity Fixtures ==========

@pytest.fixture
def user_entity_pydantic():
    """L3: 创建默认用户 Entity"""
    return UserEntityPydantic.default()


@pytest.fixture
def admin_entity_pydantic():
    """L3: 创建管理员用户 Entity"""
    return UserEntityPydantic.admin()


@pytest.fixture
def product_entity_pydantic():
    """L3: 创建默认产品 Entity"""
    return ProductEntity.default()


@pytest.fixture
def order_entity_pydantic(product_entity_pydantic):
    """L3: 创建默认订单 Entity"""
    return OrderEntity.with_product(
        product_id=product_entity_pydantic.id or 1, quantity=1
    )


# ========== L2 Builder Fixtures ==========

@pytest.fixture
def auth_builder_pydantic():
    """L2: 创建 Auth Builder"""
    builder = AuthBuilder()
    yield builder
    # 清理
    builder.cleanup()


@pytest.fixture
def auth_builder_pydantic_with_token(test_token):
    """L2: 创建带 Token 的 Auth Builder"""
    builder = AuthBuilder(token=test_token)
    yield builder
    builder.cleanup()


@pytest.fixture
def product_builder_pydantic(test_token):
    """L2: 创建 Product Builder"""
    builder = ProductBuilder(token=test_token)
    yield builder
    builder.cleanup()


@pytest.fixture
def order_builder_pydantic(test_token):
    """L2: 创建 Order Builder"""
    builder = OrderBuilder(token=test_token)
    yield builder
    builder.cleanup()


# ========== 组合 Fixtures (L3 + L2) ==========

@pytest.fixture
def created_user_pydantic(auth_builder_pydantic):
    """L3 + L2: 创建并返回用户 Entity"""
    user = UserEntityPydantic.default()
    created = auth_builder_pydantic.register(user)
    return created


@pytest.fixture
def created_product_pydantic(product_builder_pydantic):
    """L3 + L2: 创建并返回产品 Entity"""
    product = ProductEntity.default()
    created = product_builder_pydantic.create_entity(product)
    return created


@pytest.fixture
def created_order_pydantic(order_builder_pydantic, created_product_pydantic):
    """L3 + L2: 创建并返回订单 Entity"""
    order = OrderEntity.with_product(
        product_id=created_product_pydantic.id, quantity=1
    )
    created = order_builder_pydantic.create_entity(order)
    return created

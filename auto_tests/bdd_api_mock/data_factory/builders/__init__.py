# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 构造器实现层
# @Time   : 2026-04-06
# @Author : 毛鹏
"""
构造器实现层

职责：
1. 接收 L3 Entity
2. 调用 entity.to_api_payload() 获取 Dict
3. 调用 L1 API 创建/更新/删除数据
4. 更新 Entity 的响应字段
5. 记录创建的 ID，支持 cleanup() 清理

使用示例：
    # 新架构 - 使用 Pydantic Entity
    from auto_tests.bdd_api_mock.data_factory.entities import UserEntityPydantic
    from auto_tests.bdd_api_mock.data_factory.builders.auth.auth_builder_pydantic import AuthBuilder
    
    # L3: 创建 Entity
    user = UserEntityPydantic.with_credentials("testuser", "password123")
    
    # L2: 使用 Builder 创建
    builder = AuthBuilder()
    created = builder.create_entity(user)  # 或 builder.login(user)
    
    # 清理
    builder.cleanup()
"""

# 基类和上下文
from core.base import BaseBuilder, BuilderContext, PydanticBuilder, PydanticEntity
from core.enums.demo_enum import DependencyLevel

# Pydantic 新架构 Builder（L2 构造器层）
from .auth.auth_builder_pydantic import AuthBuilder as AuthBuilderPydantic
from .product.product_builder_pydantic import ProductBuilder as ProductBuilderPydantic
from .order.order_builder_pydantic import OrderBuilder as OrderBuilderPydantic

__all__ = [
    # 基类和上下文
    "BaseBuilder",
    "BuilderContext",
    "DependencyLevel",
    "PydanticBuilder",
    "PydanticEntity",
    # Pydantic 新架构 Builder（L2 构造器层）
    "AuthBuilderPydantic",
    "ProductBuilderPydantic",
    "OrderBuilderPydantic",
]

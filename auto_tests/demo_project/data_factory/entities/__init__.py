# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 实体定义层 - 数据模型和状态管理
# @Time   : 2026-03-31
# @Author : 毛鹏

"""
实体定义层

职责：
1. 定义数据模型结构
2. 管理实体生命周期（创建、更新、删除）
3. 提供数据验证方法
4. 维护实体间关系

使用示例：
    from auto_tests.demo_project.data_factory.entities import UserEntity
    
    user = UserEntity(id=1, username="test", email="test@example.com")
    user.validate()  # 验证数据有效性
"""

from core.base import BaseEntity
from core.enums.demo_enum import EntityStatus

# 原有实体（兼容旧代码）
from .budget_entity import BudgetEntity
from .ceo_approval import CEOApprovalEntity
from .dept_approval import DeptApprovalEntity
from .finance_approval import FinanceApprovalEntity
from .org_entity import OrgEntity
from .payment_entity import PaymentEntity
from .reimbursement import ReimbursementEntity
from .user import UserEntity

# Pydantic 新架构实体（L3 实体层）
from .user_pydantic import UserEntity as UserEntityPydantic
from .product_pydantic import ProductEntity
from .order_pydantic import OrderEntity

__all__ = [
    # 基类
    "BaseEntity",
    "EntityStatus",
    # 原有实体类（兼容旧代码）
    "UserEntity",
    "ReimbursementEntity",
    "DeptApprovalEntity",
    "FinanceApprovalEntity",
    "CEOApprovalEntity",
    "OrgEntity",
    "BudgetEntity",
    "PaymentEntity",
    # Pydantic 新架构实体（L3 实体层）
    "UserEntityPydantic",
    "ProductEntity",
    "OrderEntity",
]

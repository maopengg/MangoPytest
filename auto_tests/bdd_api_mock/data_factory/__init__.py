# -*- coding: utf-8 -*-
"""
Data Factory 数据工厂层

整合 entities 和 specs 到统一的数据工厂目录中，
便于管理和维护测试数据准备逻辑。
"""
from core.base.baseFactory import BaseFactory

# 导出实体层
from auto_tests.bdd_api_mock.data_factory.entities import (
    Base,
    UserEntity,
    ProductEntity,
    OrderEntity,
    DataSubmissionEntity,
    FileEntity,
    ReimbursementEntity,
    DeptApprovalEntity,
    FinanceApprovalEntity,
    CEOApprovalEntity,
    ApprovalLogEntity,
    APILogEntity,
    HealthEntity,
    AuthEntity,
)

# 导出工厂层

# 导出 Specs
from auto_tests.bdd_api_mock.data_factory.specs import (
    UserSpec,
    ProductSpec,
    OrderSpec,
    DataSubmissionSpec,
    FileSpec,
    ReimbursementSpec,
    DeptApprovalSpec,
    FinanceApprovalSpec,
    CEOApprovalSpec,
    AuthSpec,
    APILogSpec,
    HealthSpec,
    ENTITY_FACTORY_MAP,
)

__all__ = [
    # 基础
    "Base",
    "BaseFactory",
    # 实体
    "UserEntity",
    "ProductEntity",
    "OrderEntity",
    "DataSubmissionEntity",
    "FileEntity",
    "ReimbursementEntity",
    "DeptApprovalEntity",
    "FinanceApprovalEntity",
    "CEOApprovalEntity",
    "ApprovalLogEntity",
    "APILogEntity",
    "HealthEntity",
    "AuthEntity",
    # Specs
    "UserSpec",
    "ProductSpec",
    "OrderSpec",
    "DataSubmissionSpec",
    "FileSpec",
    "ReimbursementSpec",
    "DeptApprovalSpec",
    "FinanceApprovalSpec",
    "CEOApprovalSpec",
    "AuthSpec",
    "APILogSpec",
    "HealthSpec",
    "ENTITY_FACTORY_MAP",
]


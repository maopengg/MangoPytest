# -*- coding: utf-8 -*-
"""
Entities 实体层 - SQLAlchemy ORM 映射

数据工厂中的实体定义，用于测试数据准备
"""

from auto_tests.bdd_api_mock.config import Base

# 导出所有实体 - 从当前目录导入
from auto_tests.bdd_api_mock.data_factory.entities.user.user_entity import UserEntity
from auto_tests.bdd_api_mock.data_factory.entities.product.product_entity import (
    ProductEntity,
)
from auto_tests.bdd_api_mock.data_factory.entities.order.order_entity import OrderEntity
from auto_tests.bdd_api_mock.data_factory.entities.data.data_entity import (
    DataSubmissionEntity,
)
from auto_tests.bdd_api_mock.data_factory.entities.file.file_entity import FileEntity
from auto_tests.bdd_api_mock.data_factory.entities.reimbursement.reimbursement_entity import (
    ReimbursementEntity,
)
from auto_tests.bdd_api_mock.data_factory.entities.approval.dept_approval_entity import (
    DeptApprovalEntity,
)
from auto_tests.bdd_api_mock.data_factory.entities.approval.finance_approval_entity import (
    FinanceApprovalEntity,
)
from auto_tests.bdd_api_mock.data_factory.entities.approval.ceo_approval_entity import (
    CEOApprovalEntity,
)
from auto_tests.bdd_api_mock.data_factory.entities.approval.approval_log_entity import (
    ApprovalLogEntity,
)
from auto_tests.bdd_api_mock.data_factory.entities.system.api_log_entity import (
    APILogEntity,
)
from auto_tests.bdd_api_mock.data_factory.entities.system.health_entity import (
    HealthEntity,
)
from auto_tests.bdd_api_mock.data_factory.entities.auth.auth_entity import AuthEntity

__all__ = [
    "Base",
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
]

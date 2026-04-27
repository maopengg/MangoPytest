# -*- coding: utf-8 -*-
"""
Specs 数据工厂 - factory_boy

数据工厂统一入口，提供所有实体的 Factory 定义
"""

from auto_tests.bdd_api_mock.data_factory.specs.user.user_spec import UserSpec
from auto_tests.bdd_api_mock.data_factory.specs.product.product_spec import ProductSpec
from auto_tests.bdd_api_mock.data_factory.specs.order.order_spec import OrderSpec
from auto_tests.bdd_api_mock.data_factory.specs.data.data_spec import DataSubmissionSpec
from auto_tests.bdd_api_mock.data_factory.specs.file.file_spec import FileSpec
from auto_tests.bdd_api_mock.data_factory.specs.reimbursement.reimbursement_spec import (
    ReimbursementSpec,
)
from auto_tests.bdd_api_mock.data_factory.specs.approval.dept_approval_spec import (
    DeptApprovalSpec,
)
from auto_tests.bdd_api_mock.data_factory.specs.approval.finance_approval_spec import (
    FinanceApprovalSpec,
)
from auto_tests.bdd_api_mock.data_factory.specs.approval.ceo_approval_spec import (
    CEOApprovalSpec,
)
from auto_tests.bdd_api_mock.data_factory.specs.auth.auth_spec import AuthSpec
from auto_tests.bdd_api_mock.data_factory.specs.system.api_log_spec import APILogSpec
from auto_tests.bdd_api_mock.data_factory.specs.system.health_spec import HealthSpec

__all__ = [
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
]

# 实体名称到 Factory 的映射（用于步骤定义）
ENTITY_FACTORY_MAP = {
    "用户": UserSpec,
    "产品": ProductSpec,
    "订单": OrderSpec,
    "数据": DataSubmissionSpec,
    "文件": FileSpec,
    "报销": ReimbursementSpec,
    "部门审批": DeptApprovalSpec,
    "财务审批": FinanceApprovalSpec,
    "总经理审批": CEOApprovalSpec,
    "认证": AuthSpec,
    "API日志": APILogSpec,
    "健康状态": HealthSpec,
}

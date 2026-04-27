# -*- coding: utf-8 -*-
"""
Repository 数据访问层
"""

from auto_tests.bdd_api_mock.repos.user.user_repo import UserRepo
from auto_tests.bdd_api_mock.repos.product.product_repo import ProductRepo
from auto_tests.bdd_api_mock.repos.order.order_repo import OrderRepo
from auto_tests.bdd_api_mock.repos.data.data_repo import DataSubmissionRepo
from auto_tests.bdd_api_mock.repos.file.file_repo import FileRepo
from auto_tests.bdd_api_mock.repos.reimbursement.reimbursement_repo import (
    ReimbursementRepo,
)
from auto_tests.bdd_api_mock.repos.approval.dept_approval_repo import DeptApprovalRepo
from auto_tests.bdd_api_mock.repos.approval.finance_approval_repo import (
    FinanceApprovalRepo,
)
from auto_tests.bdd_api_mock.repos.approval.ceo_approval_repo import CEOApprovalRepo
from auto_tests.bdd_api_mock.repos.approval.approval_log_repo import ApprovalLogRepo
from auto_tests.bdd_api_mock.repos.system.api_log_repo import APILogRepo
from auto_tests.bdd_api_mock.repos.system.health_repo import HealthRepo
from auto_tests.bdd_api_mock.repos.auth.auth_repo import AuthRepo

__all__ = [
    "UserRepo",
    "ProductRepo",
    "OrderRepo",
    "DataSubmissionRepo",
    "FileRepo",
    "ReimbursementRepo",
    "DeptApprovalRepo",
    "FinanceApprovalRepo",
    "CEOApprovalRepo",
    "ApprovalLogRepo",
    "APILogRepo",
    "HealthRepo",
    "AuthRepo",
]

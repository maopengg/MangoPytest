# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 场景fixtures
# @Time   : 2026-03-31
# @Author : 毛鹏

"""
场景fixtures模块

提供基于新架构的场景fixtures
"""

from .scenario_fixtures import (
    login_scenario,
    register_and_login_scenario,
    logged_in_token,
)

from .approval_scenario_fixtures import (
    create_reimbursement_scenario,
    full_approval_scenario,
    rejection_scenario,
    full_approval_workflow,
    dept_rejected_workflow,
    finance_rejected_workflow,
    ceo_rejected_workflow,
)

__all__ = [
    # 通用场景
    "login_scenario",
    "register_and_login_scenario",
    "logged_in_token",
    # 审批流场景
    "create_reimbursement_scenario",
    "full_approval_scenario",
    "rejection_scenario",
    "full_approval_workflow",
    "dept_rejected_workflow",
    "finance_rejected_workflow",
    "ceo_rejected_workflow",
]

# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: fixtures注册中心 - 新架构
# @Time   : 2026-03-31
# @Author : 毛鹏

"""
fixtures注册中心 - 新架构

此文件集中注册所有fixtures，便于管理和使用。
在测试文件中只需导入此模块即可使用所有fixtures。

使用示例：
    # test_example.py
    from auto_test.demo_project.fixtures.conftest import *

    def test_with_user(test_user):
        assert test_user.id is not None
        assert test_user.username is not None

    def test_with_scenario(full_approval_workflow):
        assert full_approval_workflow.success
        reimbursement = full_approval_workflow.get_entity("reimbursement")
        assert reimbursement is not None
"""

# ========== 基础设施fixtures ==========
from .infra.client import (
    api_client,
    authenticated_client,
    api_client_with_cleanup,
)

from .infra.context import (
    test_context,
    TestContext,
)

from .infra.db import (
    db_session,
    db_transaction,
    clean_db_state,
)

# ========== 用户模块fixtures ==========
from .builders.user_fixtures import (
    user_builder,
    test_user,
    new_user,
    admin_user,
    dept_manager_user,
    finance_manager_user,
    ceo_user,
)

# ========== 报销申请模块fixtures ==========
from .builders.reimbursement_fixtures import (
    reimbursement_builder,
    created_reimbursement,
    pending_reimbursement,
    multiple_reimbursements,
)

# ========== 部门审批模块fixtures ==========
from .builders.dept_approval_fixtures import (
    dept_approval_builder,
    dept_approved_reimbursement,
    dept_rejected_reimbursement,
    dept_manager_id,
)

# ========== 财务审批模块fixtures ==========
from .builders.finance_approval_fixtures import (
    finance_approval_builder,
    finance_approved_reimbursement,
    finance_rejected_reimbursement,
    finance_manager_id,
)

# ========== 总经理审批模块fixtures ==========
from .builders.ceo_approval_fixtures import (
    ceo_approval_builder,
    fully_approved_reimbursement,
    ceo_rejected_reimbursement,
    ceo_id,
    workflow_data,
)

# ========== 产品模块fixtures ==========
from .builders.product_fixtures import (
    product_builder,
    test_product,
    product_list,
)

# ========== 订单模块fixtures ==========
from .builders.order_fixtures import (
    order_builder,
    test_order,
    order_with_product,
)

# ========== 文件模块fixtures ==========
from .builders.file_fixtures import (
    file_builder,
    temp_file,
    uploaded_file,
)

# ========== 数据模块fixtures ==========
from .builders.data_fixtures import (
    data_builder,
    submitted_data,
)

# ========== 认证模块fixtures ==========
from .builders.auth_fixtures import (
    auth_builder,
    test_token,
    registered_user,
)

# ========== 系统模块fixtures ==========
from .builders.system_fixtures import (
    system_builder,
    server_health,
    server_info,
)

# ========== 场景fixtures ==========
from .scenarios.scenario_fixtures import (
    login_scenario,
    register_and_login_scenario,
    logged_in_token,
)

from .scenarios.approval_scenario_fixtures import (
    create_reimbursement_scenario,
    full_approval_scenario,
    rejection_scenario,
    full_approval_workflow,
    dept_rejected_workflow,
    finance_rejected_workflow,
    ceo_rejected_workflow,
    approval_scenarios,
    pending_at_dept,
    pending_at_finance,
    pending_at_ceo,
    multi_level_workflows,
)

__all__ = [
    # 基础设施
    "api_client",
    "authenticated_client",
    "api_client_with_cleanup",
    "test_context",
    "TestContext",
    "db_session",
    "db_transaction",
    "clean_db_state",
    # 用户模块
    "user_builder",
    "test_user",
    "new_user",
    "admin_user",
    "dept_manager_user",
    "finance_manager_user",
    "ceo_user",
    # 报销申请模块
    "reimbursement_builder",
    "created_reimbursement",
    "pending_reimbursement",
    "multiple_reimbursements",
    # 部门审批模块
    "dept_approval_builder",
    "dept_approved_reimbursement",
    "dept_rejected_reimbursement",
    "dept_manager_id",
    # 财务审批模块
    "finance_approval_builder",
    "finance_approved_reimbursement",
    "finance_rejected_reimbursement",
    "finance_manager_id",
    # 总经理审批模块
    "ceo_approval_builder",
    "fully_approved_reimbursement",
    "ceo_rejected_reimbursement",
    "ceo_id",
    "workflow_data",
    # 产品模块
    "product_builder",
    "test_product",
    "product_list",
    # 订单模块
    "order_builder",
    "test_order",
    "order_with_product",
    # 文件模块
    "file_builder",
    "temp_file",
    "uploaded_file",
    # 数据模块
    "data_builder",
    "submitted_data",
    # 认证模块
    "auth_builder",
    "test_token",
    "registered_user",
    # 系统模块
    "system_builder",
    "server_health",
    "server_info",
    # 场景
    "login_scenario",
    "register_and_login_scenario",
    "logged_in_token",
    "create_reimbursement_scenario",
    "full_approval_scenario",
    "rejection_scenario",
    "full_approval_workflow",
    "dept_rejected_workflow",
    "finance_rejected_workflow",
    "ceo_rejected_workflow",
    "approval_scenarios",
    "pending_at_dept",
    "pending_at_finance",
    "pending_at_ceo",
    "multi_level_workflows",
]

# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: pytest配置文件 - 新架构
# @Time   : 2026-03-31
# @Author : 毛鹏


# 导入 Allure 集成（从 pe.reporting）
from pe.reporting import (
    # pytest 钩子
    pytest_configure as _allure_pytest_configure,
    # fixtures
    allure_context,
    allure_lineage,
    allure_variant,
    # 装饰器
    allure_feature,
    allure_story,
    allure_severity,
    allure_tag,
    allure_label,
    # 增强器
    LineageEnhancer,
    MatrixEnhancer,
    StateMachineEnhancer,
)

# 导入 fixtures
from auto_test.demo_project.fixtures.conftest import (
    # 基础设施
    api_client,
    authenticated_client,
    api_client_with_cleanup,
    test_context,
    TestContext,
    TestContextRecord,
    ValueExpectation,
    EventExpectation,
    db_session,
    db_transaction,
    clean_db_state,
    # 用户模块
    user_builder,
    test_user,
    new_user,
    admin_user,
    dept_manager_user,
    finance_manager_user,
    ceo_user,
    # 报销申请模块
    reimbursement_builder,
    created_reimbursement,
    pending_reimbursement,
    multiple_reimbursements,
    # C模块构造器
    org_builder,
    budget_builder,
    # 部门审批模块
    dept_approval_builder,
    dept_approved_reimbursement,
    dept_rejected_reimbursement,
    dept_manager_id,
    # 财务审批模块
    finance_approval_builder,
    finance_approved_reimbursement,
    finance_rejected_reimbursement,
    finance_manager_id,
    # 总经理审批模块
    ceo_approval_builder,
    fully_approved_reimbursement,
    ceo_rejected_reimbursement,
    ceo_id,
    workflow_data,
    # 产品模块
    product_builder,
    test_product,
    product_list,
    # 订单模块
    order_builder,
    test_order,
    order_with_product,
    # 文件模块
    file_builder,
    temp_file,
    uploaded_file,
    # 数据模块
    data_builder,
    submitted_data,
    # 认证模块
    auth_builder,
    test_token,
    registered_user,
    # 系统模块
    system_builder,
    server_health,
    server_info,
    # 场景
    login_scenario,
    register_and_login_scenario,
    logged_in_token,
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


# 项目级别的pytest配置
def pytest_configure(config):
    """pytest配置钩子"""
    # 添加自定义标记
    config.addinivalue_line("markers", "approval_flow: 标记审批流相关测试")
    config.addinivalue_line("markers", "entity_test: 标记实体相关测试")
    config.addinivalue_line("markers", "scenario_test: 标记场景相关测试")
    
    # 初始化 Allure 集成
    _allure_pytest_configure(config)


def pytest_collection_modifyitems(config, items):
    """测试收集完成后的钩子"""
    # 可以在这里对测试项进行排序或过滤
    pass


# 导出所有公共接口
__all__ = [
    # Allure fixtures
    "allure_context",
    "allure_lineage",
    "allure_variant",
    # Allure 装饰器
    "allure_feature",
    "allure_story",
    "allure_severity",
    "allure_tag",
    "allure_label",
    # Allure 增强器
    "LineageEnhancer",
    "MatrixEnhancer",
    "StateMachineEnhancer",
    # 基础设施
    "api_client",
    "authenticated_client",
    "api_client_with_cleanup",
    "test_context",
    "TestContext",
    "TestContextRecord",
    "ValueExpectation",
    "EventExpectation",
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
    # C模块构造器
    "org_builder",
    "budget_builder",
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

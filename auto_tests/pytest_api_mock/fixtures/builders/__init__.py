# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: Builder Fixtures - 构造器 fixtures
# @Time   : 2026-04-01
# @Author : 毛鹏

"""
Builder Fixtures 模块

提供预配置的构造器 fixtures

分层结构：
- 基础层: user (user_builder)
- 认证层: auth (auth_builder, test_token)
- 预算层: budget (org_builder, budget_builder)
- 数据层: data (data_builder, test_data)
- 文件层: file (file_builder, uploaded_file)
- 订单层: order (order_builder, test_order)
- 产品层: product (product_builder, test_product)
- 系统层: system (system_builder, system_status)
- 报销层: reimbursement (reimb_builder, approved_reimbursement)
- 付款层: payment (payment_builder, paid_payment)
- 部门审批层: dept_approval (dept_approval_builder, dept_approved_reimbursement)
- 财务审批层: finance_approval (finance_approval_builder, finance_approved_reimbursement)
- 总经理审批层: ceo_approval (ceo_approval_builder, fully_approved_reimbursement)
"""

# 基础层
from .user import user_builder

# 认证层
from .auth import auth_builder, test_token, registered_user

# 预算层
from .budget import budget_builder, org_builder

# 数据层
from .data import data_builder, test_data, data_list

# 文件层
from .file import file_builder, uploaded_file, file_list

# 订单层
from .order import order_builder, test_order, order_list, paid_order

# 产品层
from .product import product_builder, test_product, product_list, out_of_stock_product

# 系统层
from .system import system_builder, system_status, system_config

# 报销层
from .reimbursement import reimb_builder, approved_reimbursement

# 付款层
from .payment import payment_builder, paid_payment

# 部门审批层
from .dept_approval import dept_approval_builder, dept_approved_reimbursement, dept_rejected_reimbursement, dept_manager_id

# 财务审批层
from .finance_approval import finance_approval_builder, finance_approved_reimbursement, finance_rejected_reimbursement, finance_manager_id

# 总经理审批层
from .ceo_approval import ceo_approval_builder, fully_approved_reimbursement, ceo_rejected_reimbursement, ceo_id, ceo_approved_reimbursement, workflow_data


__all__ = [
    # 基础层
    "user_builder",
    # 认证层
    "auth_builder",
    "test_token",
    "registered_user",
    # 预算层
    "org_builder",
    "budget_builder",
    # 数据层
    "data_builder",
    "test_data",
    "data_list",
    # 文件层
    "file_builder",
    "uploaded_file",
    "file_list",
    # 订单层
    "order_builder",
    "test_order",
    "order_list",
    "paid_order",
    # 产品层
    "product_builder",
    "test_product",
    "product_list",
    "out_of_stock_product",
    # 系统层
    "system_builder",
    "system_status",
    "system_config",
    # 报销层
    "reimb_builder",
    "approved_reimbursement",
    # 付款层
    "payment_builder",
    "paid_payment",
    # 部门审批层
    "dept_approval_builder",
    "dept_approved_reimbursement",
    "dept_rejected_reimbursement",
    "dept_manager_id",
    # 财务审批层
    "finance_approval_builder",
    "finance_approved_reimbursement",
    "finance_rejected_reimbursement",
    "finance_manager_id",
    # 总经理审批层
    "ceo_approval_builder",
    "fully_approved_reimbursement",
    "ceo_rejected_reimbursement",
    "ceo_id",
    "ceo_approved_reimbursement",
    "workflow_data",
]

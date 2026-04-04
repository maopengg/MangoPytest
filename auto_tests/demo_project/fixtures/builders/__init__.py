# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: Builder Fixtures - 构造器 fixtures
# @Time   : 2026-04-01
# @Author : 毛鹏

"""
Builder Fixtures 模块

提供预配置的构造器 fixtures

分层结构：
- D模块（基础层）: user_builder
- C模块（预算层）: org_builder, budget_builder
- B模块（报销层）: reimb_builder
- A模块（付款层）: payment_builder
"""

from .a_fixtures import (
    payment_builder,
    paid_payment,
)
from .b_fixtures import (
    reimb_builder,
    approved_reimbursement,
)
from .c_fixtures import *
from .d_fixtures import (
    user_builder,
)

__all__ = [
    # D模块
    "user_builder",
    # C模块
    "org_builder",
    "budget_builder",
    # B模块
    "reimb_builder",
    "approved_reimbursement",
    # A模块
    "payment_builder",
    "paid_payment",
]

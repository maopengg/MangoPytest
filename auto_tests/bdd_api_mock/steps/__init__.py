# -*- coding: utf-8 -*-
"""
Steps 步骤定义层

项目特定的步骤定义，按功能分类：
- auth: 认证相关步骤（项目特定）

通用步骤已从 core.bdd 导入
"""

# 导出认证步骤
from auto_tests.bdd_api_mock.steps.auth import (
    user_logged_in_step,
    admin_logged_in_step,
    manager_logged_in_step,
    finance_logged_in_step,
    ceo_logged_in_step,
    user_login_step,
    login_should_succeed,
    login_should_fail,
    should_return_error_code,
)

__all__ = [
    # 认证步骤
    "user_logged_in_step",
    "admin_logged_in_step",
    "manager_logged_in_step",
    "finance_logged_in_step",
    "ceo_logged_in_step",
    "user_login_step",
    "login_should_succeed",
    "login_should_fail",
    "should_return_error_code",
]

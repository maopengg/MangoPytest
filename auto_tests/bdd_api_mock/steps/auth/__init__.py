# -*- coding: utf-8 -*-
"""
认证相关步骤

提供登录、权限验证等步骤定义
"""

from auto_tests.bdd_api_mock.steps.auth.login import (
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

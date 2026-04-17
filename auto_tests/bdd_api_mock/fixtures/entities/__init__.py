# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: Entity Fixtures - 实体 fixtures
# @Time   : 2026-04-01
# @Author : 毛鹏

"""
Entity Fixtures 模块

提供预配置的实体 fixtures
"""

from .org_fixtures import (
    default_org,
    large_org,
    small_org,
    dept_org,
)
from .user_fixtures import (
    admin_user,
    normal_user,
    locked_user,
    employee_user,
    manager_user,
    finance_user,
    ceo_user,
)

__all__ = [
    # User fixtures
    "admin_user",
    "normal_user",
    "locked_user",
    "employee_user",
    "manager_user",
    "finance_user",
    "ceo_user",
    # Org fixtures
    "default_org",
    "large_org",
    "small_org",
    "dept_org",
]

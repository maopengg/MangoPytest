# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: User Entity Fixtures - 用户实体 fixtures
# @Time   : 2026-04-01
# @Author : 毛鹏

"""
User Entity Fixtures 模块

提供预配置的用户实体 fixtures：
- admin_user: 管理员用户
- normal_user: 普通用户
- locked_user: 已锁定用户
- employee_user: 员工用户

使用示例：
    def test_with_admin(admin_user):
        assert admin_user.role == "admin"
        assert admin_user.is_active()
"""

import pytest

from auto_tests.pytest_api_mock.data_factory.entities import UserEntity


@pytest.fixture
def admin_user() -> UserEntity:
    """
    管理员用户 fixture
    
    返回一个预配置的管理员用户实体
    
    使用示例：
        def test_admin_access(admin_user):
            assert admin_user.role == "admin"
    """
    return UserEntity(
        username="admin",
        email="admin@example.com",
        role="admin",
        status="active"
    )


@pytest.fixture
def normal_user() -> UserEntity:
    """
    普通用户 fixture
    
    返回一个预配置的普通用户实体
    """
    return UserEntity(
        username="normal_user",
        email="user@example.com",
        role="user",
        status="active"
    )


@pytest.fixture
def locked_user() -> UserEntity:
    """
    已锁定用户 fixture
    
    返回一个预配置的已锁定用户实体
    """
    return UserEntity(
        username="locked_user",
        email="locked@example.com",
        role="user",
        status="locked"
    )


@pytest.fixture
def employee_user() -> UserEntity:
    """
    员工用户 fixture
    
    返回一个预配置的员工用户实体
    """
    return UserEntity(
        username="employee_001",
        email="employee@example.com",
        role="employee",
        status="active",
        department="研发部"
    )


@pytest.fixture
def manager_user() -> UserEntity:
    """
    经理用户 fixture
    
    返回一个预配置的经理用户实体（用于部门审批）
    """
    return UserEntity(
        username="manager_001",
        email="manager@example.com",
        role="manager",
        status="active",
        department="研发部"
    )


@pytest.fixture
def finance_user() -> UserEntity:
    """
    财务用户 fixture
    
    返回一个预配置的财务用户实体（用于财务审批）
    """
    return UserEntity(
        username="finance_001",
        email="finance@example.com",
        role="finance",
        status="active",
        department="财务部"
    )


@pytest.fixture
def ceo_user() -> UserEntity:
    """
    CEO用户 fixture
    
    返回一个预配置的CEO用户实体（用于CEO审批）
    """
    return UserEntity(
        username="ceo_001",
        email="ceo@example.com",
        role="ceo",
        status="active",
        department="管理层"
    )


# 导出
__all__ = [
    "admin_user",
    "normal_user",
    "locked_user",
    "employee_user",
    "manager_user",
    "finance_user",
    "ceo_user",
]

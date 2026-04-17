# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: User Fixtures - 用户构造器 fixtures
# @Time   : 2026-04-01
# @Author : 毛鹏

"""
User Fixtures 模块

提供用户构造器 fixtures：
- user_builder: 用户构造器
- test_user: 测试用户
- admin_user: 管理员用户
- dept_manager_user: 部门经理用户
- finance_manager_user: 财务经理用户
- ceo_user: CEO用户

用户层是最底层，无依赖
"""

from typing import Generator

import pytest

from auto_tests.bdd_api_mock.data_factory.builders.user import UserBuilder
from auto_tests.bdd_api_mock.data_factory.entities import UserEntity
from core.base import BuilderContext


@pytest.fixture
def user_builder(test_token) -> Generator[UserBuilder, None, None]:
    """
    用户构造器 fixture

    返回一个配置好的 UserBuilder 实例
    测试结束后自动清理

    使用示例：
        def test_create_user(user_builder):
            user = user_builder.create(username="test")
            assert user.id is not None
    """
    context = BuilderContext(cascade_cleanup=False, auto_prepare_deps=True)
    builder = UserBuilder(token=test_token, context=context)

    yield builder

    # 自动清理
    builder.cleanup()


@pytest.fixture
def test_user(test_token) -> UserEntity:
    """
    测试用户 fixture

    返回一个已创建的测试用户实体

    使用示例：
        def test_with_user(test_user):
            assert test_user.id is not None
            assert test_user.username is not None
    """
    # 返回 mock 用户
    return UserEntity(
        id=1,
        username="testuser",
        email="test@example.com",
        full_name="Test User",
        password="password123",
        role="user",
        status="active",
    )


@pytest.fixture
def admin_user(test_token) -> UserEntity:
    """
    管理员用户 fixture

    返回一个管理员用户实体
    注意：当前后端注册接口不支持自定义角色，所有用户角色都是"user"
    """
    # 返回 mock 用户 - 角色为 "user" 以匹配后端行为
    return UserEntity(
        id=2,
        username="admin",
        email="admin@example.com",
        full_name="Admin User",
        password="admin123",
        role="user",  # 后端返回的是 "user"
        status="active",
    )


@pytest.fixture
def dept_manager_user(test_token) -> UserEntity:
    """
    部门经理用户 fixture

    返回一个部门经理用户实体
    注意：当前后端注册接口不支持自定义角色，所有用户角色都是"user"
    """
    # 返回 mock 用户 - 角色为 "user" 以匹配后端行为
    return UserEntity(
        id=3,
        username="dept_manager",
        email="dept@example.com",
        full_name="Department Manager",
        password="manager123",
        role="user",  # 后端返回的是 "user"
        status="active",
    )


@pytest.fixture
def finance_manager_user(test_token) -> UserEntity:
    """
    财务经理用户 fixture

    返回一个财务经理用户实体
    注意：当前后端注册接口不支持自定义角色，所有用户角色都是"user"
    """
    # 返回 mock 用户 - 角色为 "user" 以匹配后端行为
    return UserEntity(
        id=4,
        username="finance_manager",
        email="finance@example.com",
        full_name="Finance Manager",
        password="finance123",
        role="user",  # 后端返回的是 "user"
        status="active",
    )


@pytest.fixture
def ceo_user(test_token) -> UserEntity:
    """
    CEO用户 fixture

    返回一个CEO用户实体
    注意：当前后端注册接口不支持自定义角色，所有用户角色都是"user"
    """
    # 返回 mock 用户 - 角色为 "user" 以匹配后端行为
    return UserEntity(
        id=5,
        username="ceo",
        email="ceo@example.com",
        full_name="CEO",
        password="ceo123",
        role="user",  # 后端返回的是 "user"
        status="active",
    )

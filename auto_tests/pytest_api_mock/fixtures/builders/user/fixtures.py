# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: User Fixtures - 用户构造器 fixtures
# @Time   : 2026-04-01
# @Author : 毛鹏

"""
User Fixtures 模块

提供用户构造器 fixtures：
- user_builder: 用户构造器
- test_user: 测试用户 (mock，对应 testuser)
- admin_user: 管理员用户 (通过数据工厂创建)
- dept_manager_user: 部门经理用户 (通过数据工厂创建)
- finance_manager_user: 财务经理用户 (通过数据工厂创建)
- ceo_user: CEO用户 (通过数据工厂创建)

注意：testuser 只能用于登录，不能修改和删除
其他用户通过数据工厂创建，可以进行修改和删除操作
"""

import uuid
from typing import Generator

import pytest

from auto_tests.pytest_api_mock.data_factory.builders.auth import AuthBuilder
from auto_tests.pytest_api_mock.data_factory.builders.user import UserBuilder
from auto_tests.pytest_api_mock.data_factory.entities import UserEntity
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

    返回 testuser 的 mock 数据
    注意：testuser 只能用于登录，不能修改和删除

    使用示例：
        def test_with_user(test_user):
            assert test_user.id is not None
            assert test_user.username is not None
    """
    # 返回 mock 用户 - testuser 是系统预设用户，ID=1
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
def admin_user(test_token) -> Generator[UserEntity, None, None]:
    """
    管理员用户 fixture

    通过数据工厂创建真实用户
    可以进行修改和删除操作
    """
    auth_builder = AuthBuilder(token=test_token)
    
    # 使用随机后缀避免用户名冲突
    suffix = uuid.uuid4().hex[:6]
    
    # 创建真实用户
    user_data = auth_builder.register(
        username=f"admin_{suffix}",
        email=f"admin_{suffix}@example.com",
        full_name="Admin Test User",
        password="admin123",
        role="admin"
    )
    
    # 转换为 UserEntity
    user = UserEntity(
        id=user_data.get("id"),
        username=user_data.get("username"),
        email=user_data.get("email"),
        full_name=user_data.get("full_name"),
        password="admin123",
        role=user_data.get("role", "user"),
        status="active",
    )
    
    yield user
    
    # 清理：删除创建的用户
    if user.id:
        user_builder = UserBuilder(token=test_token)
        user_builder.delete(user_id=user.id)


@pytest.fixture
def dept_manager_user(test_token) -> Generator[UserEntity, None, None]:
    """
    部门经理用户 fixture

    通过数据工厂创建真实用户
    可以进行修改和删除操作
    """
    auth_builder = AuthBuilder(token=test_token)
    
    # 使用随机后缀避免用户名冲突
    suffix = uuid.uuid4().hex[:6]
    
    # 创建真实用户
    user_data = auth_builder.register(
        username=f"dept_{suffix}",
        email=f"dept_{suffix}@example.com",
        full_name="Department Manager Test",
        password="dept123",
        role="dept_manager"
    )
    
    # 转换为 UserEntity
    user = UserEntity(
        id=user_data.get("id"),
        username=user_data.get("username"),
        email=user_data.get("email"),
        full_name=user_data.get("full_name"),
        password="dept123",
        role=user_data.get("role", "user"),
        status="active",
    )
    
    yield user
    
    # 清理：删除创建的用户
    if user.id:
        user_builder = UserBuilder(token=test_token)
        user_builder.delete(user_id=user.id)


@pytest.fixture
def finance_manager_user(test_token) -> Generator[UserEntity, None, None]:
    """
    财务经理用户 fixture

    通过数据工厂创建真实用户
    可以进行修改和删除操作
    """
    auth_builder = AuthBuilder(token=test_token)
    
    # 使用随机后缀避免用户名冲突
    suffix = uuid.uuid4().hex[:6]
    
    # 创建真实用户
    user_data = auth_builder.register(
        username=f"finance_{suffix}",
        email=f"finance_{suffix}@example.com",
        full_name="Finance Manager Test",
        password="finance123",
        role="finance_manager"
    )
    
    # 转换为 UserEntity
    user = UserEntity(
        id=user_data.get("id"),
        username=user_data.get("username"),
        email=user_data.get("email"),
        full_name=user_data.get("full_name"),
        password="finance123",
        role=user_data.get("role", "user"),
        status="active",
    )
    
    yield user
    
    # 清理：删除创建的用户
    if user.id:
        user_builder = UserBuilder(token=test_token)
        user_builder.delete(user_id=user.id)


@pytest.fixture
def ceo_user(test_token) -> Generator[UserEntity, None, None]:
    """
    CEO用户 fixture

    通过数据工厂创建真实用户
    可以进行修改和删除操作
    """
    auth_builder = AuthBuilder(token=test_token)
    
    # 使用随机后缀避免用户名冲突
    suffix = uuid.uuid4().hex[:6]
    
    # 创建真实用户
    user_data = auth_builder.register(
        username=f"ceo_{suffix}",
        email=f"ceo_{suffix}@example.com",
        full_name="CEO Test",
        password="ceo123",
        role="ceo"
    )
    
    # 转换为 UserEntity
    user = UserEntity(
        id=user_data.get("id"),
        username=user_data.get("username"),
        email=user_data.get("email"),
        full_name=user_data.get("full_name"),
        password="ceo123",
        role=user_data.get("role", "user"),
        status="active",
    )
    
    yield user
    
    # 清理：删除创建的用户
    if user.id:
        user_builder = UserBuilder(token=test_token)
        user_builder.delete(user_id=user.id)

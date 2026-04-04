# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 用户模块 fixtures - 新架构
# @Time   : 2026-03-31
# @Author : 毛鹏
from typing import Generator, Dict, Any

import pytest

from auto_tests.demo_project.data_factory.builders import UserBuilder
from auto_tests.demo_project.data_factory.entities import UserEntity


@pytest.fixture(scope="function")
def user_builder(test_token) -> UserBuilder:
    """
    用户构造器 fixture
    提供UserBuilder实例用于创建用户数据
    """
    return UserBuilder(token=test_token)


@pytest.fixture(scope="function")
def test_user(user_builder) -> Generator[UserEntity, None, None]:
    """
    测试用户 fixture
    创建一个标准测试用户
    """
    entity = user_builder.create()
    if not entity:
        pytest.skip("无法创建测试用户")

    yield entity

    # 清理
    user_builder.delete(entity)


@pytest.fixture(scope="function")
def new_user(user_builder) -> Generator[Dict[str, Any], None, None]:
    """
    新用户 fixture（返回字典格式）
    用于需要字典格式的测试场景
    """
    entity = user_builder.create()
    if not entity:
        pytest.skip("无法创建测试用户")

    yield entity.to_dict()

    # 清理
    user_builder.delete(entity)


@pytest.fixture(scope="function")
def admin_user(user_builder) -> Generator[UserEntity, None, None]:
    """
    管理员用户 fixture
    创建具有admin角色的用户
    """
    entity = user_builder.create(role="admin")
    if not entity:
        pytest.skip("无法创建管理员用户")

    yield entity

    # 清理
    user_builder.delete(entity)


@pytest.fixture(scope="function")
def dept_manager_user(user_builder) -> Generator[UserEntity, None, None]:
    """
    部门经理用户 fixture
    用于审批流测试
    """
    entity = user_builder.create(role="dept_manager")
    if not entity:
        pytest.skip("无法创建部门经理用户")

    yield entity

    # 清理
    user_builder.delete(entity)


@pytest.fixture(scope="function")
def finance_manager_user(user_builder) -> Generator[UserEntity, None, None]:
    """
    财务经理用户 fixture
    用于审批流测试
    """
    entity = user_builder.create(role="finance_manager")
    if not entity:
        pytest.skip("无法创建财务经理用户")

    yield entity

    # 清理
    user_builder.delete(entity)


@pytest.fixture(scope="function")
def ceo_user(user_builder) -> Generator[UserEntity, None, None]:
    """
    CEO用户 fixture
    用于审批流测试
    """
    entity = user_builder.create(role="ceo")
    if not entity:
        pytest.skip("无法创建CEO用户")

    yield entity

    # 清理
    user_builder.delete(entity)

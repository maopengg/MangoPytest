# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 用户模块 fixtures
# @Time   : 2026-03-31
# @Author : 毛鹏
import pytest
from typing import Generator, Dict, Any

from auto_test.demo_project.data_factory.builders.user import UserBuilder


@pytest.fixture(scope="session")
def user_builder(test_token) -> UserBuilder:
    """用户构造器 fixture"""
    return UserBuilder(token=test_token)


@pytest.fixture(scope="function")
def test_user(user_builder) -> Generator[Dict[str, Any], None, None]:
    """
    测试用户 fixture
    获取第一个可用用户
    """
    users = user_builder.get_all()
    if not users:
        pytest.skip("没有可用的测试用户")
    
    yield users[0]


@pytest.fixture(scope="function")
def new_user(user_builder, auth_builder) -> Generator[Dict[str, Any], None, None]:
    """
    新用户 fixture
    通过注册创建一个新用户
    """
    # 使用auth_builder创建用户
    from auto_test.demo_project.data_factory.builders.auth import AuthBuilder
    auth = AuthBuilder()
    user = auth.register()
    
    if not user:
        pytest.skip("无法创建测试用户")
    
    yield user
    
    # 清理
    try:
        user_builder.delete(user.get('id'))
    except Exception:
        pass

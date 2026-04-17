# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: Reimbursement Fixtures - 报销单构造器 fixtures
# @Time   : 2026-04-01
# @Author : 毛鹏

"""
Reimbursement Fixtures 模块

提供报销单构造器 fixtures：
- reimb_builder: 报销单构造器
- approved_reimbursement: 已审批报销单
- pending_reimbursement: 待审批报销单
- created_reimbursement: 已创建报销单

报销单依赖预算（Budget）和用户/组织（User/Org）
"""

from typing import Generator, Dict, Any

import pytest

from auto_tests.pytest_api_mock.data_factory.builders.reimbursement import ReimbursementBuilder
from auto_tests.pytest_api_mock.data_factory.entities import ReimbursementEntity
from core.base import BuilderContext


@pytest.fixture
def reimb_builder(test_token) -> Generator[ReimbursementBuilder, None, None]:
    """
    报销单构造器 fixture
    
    返回一个配置好的 ReimbursementBuilder 实例
    测试结束后自动清理
    
    使用示例：
        def test_create_reimbursement(reimb_builder):
            reimb = reimb_builder.create(user_id=1, amount=1000)
            assert reimb.id is not None
    """
    context = BuilderContext(cascade_cleanup=False, auto_prepare_deps=True)
    builder = ReimbursementBuilder(
        token=test_token,
        context=context
    )

    yield builder

    # 自动清理
    builder.cleanup()


@pytest.fixture
def approved_reimbursement(reimb_builder, employee_user):
    """
    已审批报销单 fixture
    
    返回一个已审批通过的报销单
    
    使用示例：
        def test_with_approved_reimb(approved_reimbursement):
            assert approved_reimbursement.status == "approved"
    """
    reimb = reimb_builder.create_approved(
        user_id=employee_user.id if hasattr(employee_user, 'id') else 1,
        amount=5000,
        reason="测试报销"
    )
    return reimb


@pytest.fixture
def pending_reimbursement(reimb_builder, employee_user) -> ReimbursementEntity:
    """
    待审批报销单 fixture
    
    返回一个待审批的报销单实体
    
    使用示例：
        def test_with_pending_reimb(pending_reimbursement):
            assert pending_reimbursement.status == "pending"
    """
    reimb = reimb_builder.create(
        user_id=employee_user.id if hasattr(employee_user, 'id') else 1,
        amount=1000,
        reason="待审批测试"
    )
    return reimb


@pytest.fixture
def created_reimbursement(reimb_builder, employee_user) -> ReimbursementEntity:
    """
    已创建报销单 fixture
    
    返回一个已创建的报销单实体（未提交审批）
    
    使用示例：
        def test_with_created_reimb(created_reimbursement):
            assert created_reimbursement.id is not None
    """
    reimb = reimb_builder.create(
        user_id=employee_user.id if hasattr(employee_user, 'id') else 1,
        amount=2000,
        reason="已创建测试"
    )
    return reimb


@pytest.fixture
def employee_user(test_token):
    """
    普通员工用户 fixture
    
    返回一个普通员工用户
    """
    from auto_tests.pytest_api_mock.data_factory.builders.auth import AuthBuilder
    from auto_tests.pytest_api_mock.data_factory.entities import UserEntity
    
    auth_builder = AuthBuilder(token=test_token)
    user = auth_builder.register(role="employee")
    if user:
        if isinstance(user, dict):
            return UserEntity(
                id=user.get("id"),
                username=user.get("username"),
                email=user.get("email"),
                full_name=user.get("full_name"),
                password=user.get("password", ""),
                role="employee",
                status=user.get("status", "active"),
            )
        return user
    # 如果注册失败，创建一个 mock 用户
    return UserEntity(
        id=10,
        username="employee",
        email="employee@example.com",
        full_name="Employee",
        password="employee123",
        role="employee",
        status="active",
    )

# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 财务审批模块fixtures (B级)
# @Time   : 2026-03-31
# @Author : 毛鹏
import uuid
from typing import Any, Generator

import pytest

from auto_tests.pytest_api_mock.data_factory.builders.auth import AuthBuilder
from auto_tests.pytest_api_mock.data_factory.builders.finance_approval import FinanceApprovalBuilder
from auto_tests.pytest_api_mock.data_factory.builders.user import UserBuilder
from auto_tests.pytest_api_mock.data_factory.entities import UserEntity


@pytest.fixture
def finance_approval_builder(authenticated_client) -> Generator[FinanceApprovalBuilder, Any, None]:
    """
    财务审批Builder Fixture
    提供FinanceApprovalBuilder实例用于创建和管理财务审批数据

    使用示例:
        def test_example(finance_approval_builder, dept_approved_reimbursement):
            approval = finance_approval_builder.approve(
                dept_approved_reimbursement["reimbursement"]["id"],
                dept_approved_reimbursement["dept_approval"]["id"]
            )
            assert approval is not None
    """
    builder = FinanceApprovalBuilder(token=authenticated_client.token)
    yield builder
    # 清理创建的数据
    builder.cleanup()


def _entity_to_dict(entity):
    """将实体转换为字典"""
    if entity is None:
        return None
    if hasattr(entity, "__dict__"):
        result = entity.__dict__.copy()
        result.pop("_is_new", None)
        result.pop("_is_deleted", None)
        return result
    return str(entity)


@pytest.fixture
def finance_manager_user(authenticated_client) -> Generator[UserEntity, None, None]:
    """
    财务经理用户 Fixture
    通过数据工厂创建真实的财务经理用户
    """
    auth_builder = AuthBuilder(token=authenticated_client.token)
    
    # 使用随机后缀避免用户名冲突
    suffix = uuid.uuid4().hex[:6]
    
    # 创建真实用户
    user_data = auth_builder.register(
        username=f"finance_mgr_{suffix}",
        email=f"finance_mgr_{suffix}@example.com",
        full_name="Finance Manager",
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
        user_builder = UserBuilder(token=authenticated_client.token)
        user_builder.delete(user_id=user.id)


@pytest.fixture
def finance_manager_id(finance_manager_user) -> int:
    """
    财务经理用户ID Fixture
    返回通过数据工厂创建的财务经理用户ID
    """
    return finance_manager_user.id


@pytest.fixture
def finance_approved_reimbursement(
        reimbursement_builder, dept_approval_builder, finance_approval_builder,
        dept_manager_id, finance_manager_id
) -> dict:
    """
    财务审批通过的报销申请Fixture
    提供D级+C级+B级完整数据（财务已审批通过）

    使用示例:
        def test_finance_approved(finance_approved_reimbursement):
            assert finance_approved_reimbursement["reimbursement"]["status"] == "finance_approved"
            assert finance_approved_reimbursement["finance_approval"]["status"] == "approved"
    """
    # D级：创建报销申请
    reimbursement = reimbursement_builder.create(
        user_id=1, amount=2000.00, reason="财务审批通过测试"
    )

    # C级：部门审批通过
    dept_approval = dept_approval_builder.approve(reimbursement.id, approver_id=dept_manager_id)

    # B级：财务审批通过
    finance_approval = finance_approval_builder.approve(
        reimbursement.id, dept_approval.id, approver_id=finance_manager_id
    )

    return {
        "reimbursement": _entity_to_dict(reimbursement),
        "dept_approval": _entity_to_dict(dept_approval),
        "finance_approval": _entity_to_dict(finance_approval),
        "status": "finance_approved",
    }


@pytest.fixture
def finance_rejected_reimbursement(
        reimbursement_builder, dept_approval_builder, finance_approval_builder,
        dept_manager_id, finance_manager_id
) -> dict:
    """
    被财务拒绝的报销申请Fixture
    提供D级+C级+B级(拒绝)完整数据
    """
    # D级：创建报销申请
    reimbursement = reimbursement_builder.create(
        user_id=1, amount=20000.00, reason="财务拒绝测试"
    )

    # C级：部门审批通过
    dept_approval = dept_approval_builder.approve(reimbursement.id, approver_id=dept_manager_id)

    # B级：财务审批拒绝
    finance_approval = finance_approval_builder.reject(
        reimbursement.id, dept_approval.id, approver_id=finance_manager_id, comment="发票不符合规定"
    )

    return {
        "reimbursement": _entity_to_dict(reimbursement),
        "dept_approval": _entity_to_dict(dept_approval),
        "finance_approval": _entity_to_dict(finance_approval),
        "status": "finance_rejected",
    }

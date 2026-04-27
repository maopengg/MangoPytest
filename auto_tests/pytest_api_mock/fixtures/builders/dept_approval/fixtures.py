# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 部门审批模块fixtures (C级)
# @Time   : 2026-03-31
# @Author : 毛鹏
import uuid
from typing import Any, Generator

import pytest

from auto_tests.pytest_api_mock.data_factory.builders.auth import AuthBuilder
from auto_tests.pytest_api_mock.data_factory.builders.dept_approval import DeptApprovalBuilder
from auto_tests.pytest_api_mock.data_factory.builders.user import UserBuilder
from auto_tests.pytest_api_mock.data_factory.entities import UserEntity


@pytest.fixture
def dept_approval_builder(authenticated_client) -> Generator[DeptApprovalBuilder, Any, None]:
    """
    部门审批Builder Fixture
    提供DeptApprovalBuilder实例用于创建和管理部门审批数据

    使用示例:
        def test_example(dept_approval_builder, reimbursement):
            approval = dept_approval_builder.approve(reimbursement["id"])
            assert approval is not None
    """
    builder = DeptApprovalBuilder(token=authenticated_client.token)
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
def dept_manager_user(authenticated_client) -> Generator[UserEntity, None, None]:
    """
    部门经理用户 Fixture
    通过数据工厂创建真实的部门经理用户
    """
    auth_builder = AuthBuilder(token=authenticated_client.token)
    
    # 使用随机后缀避免用户名冲突
    suffix = uuid.uuid4().hex[:6]
    
    # 创建真实用户
    user_data = auth_builder.register(
        username=f"dept_mgr_{suffix}",
        email=f"dept_mgr_{suffix}@example.com",
        full_name="Department Manager",
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
        user_builder = UserBuilder(token=authenticated_client.token)
        user_builder.delete(user_id=user.id)


@pytest.fixture
def dept_manager_id(dept_manager_user) -> int:
    """
    部门经理用户ID Fixture
    返回通过数据工厂创建的部门经理用户ID
    """
    return dept_manager_user.id


@pytest.fixture
def dept_approved_reimbursement(reimbursement_builder, dept_approval_builder, dept_manager_id) -> dict:
    """
    部门审批通过的报销申请Fixture
    提供D级+C级完整数据（部门已审批通过）

    使用示例:
        def test_dept_approved(dept_approved_reimbursement):
            assert dept_approved_reimbursement["reimbursement"]["status"] == "dept_approved"
            assert dept_approved_reimbursement["dept_approval"]["status"] == "approved"
    """
    # D级：创建报销申请
    reimbursement = reimbursement_builder.create(
        user_id=1, amount=1000.00, reason="部门审批通过测试"
    )

    # C级：部门审批通过
    dept_approval = dept_approval_builder.approve(reimbursement.id, approver_id=dept_manager_id)

    return {
        "reimbursement": _entity_to_dict(reimbursement),
        "dept_approval": _entity_to_dict(dept_approval),
        "status": "dept_approved",
    }


@pytest.fixture
def dept_rejected_reimbursement(reimbursement_builder, dept_approval_builder, dept_manager_id) -> dict:
    """
    被部门拒绝的报销申请Fixture
    提供D级+C级(拒绝)完整数据
    """
    # D级：创建报销申请
    reimbursement = reimbursement_builder.create(
        user_id=1, amount=50000.00, reason="部门拒绝测试"
    )

    # C级：部门审批拒绝
    dept_approval = dept_approval_builder.reject(
        reimbursement.id, approver_id=dept_manager_id, comment="金额超出部门预算"
    )

    return {
        "reimbursement": _entity_to_dict(reimbursement),
        "dept_approval": _entity_to_dict(dept_approval),
        "status": "dept_rejected",
    }

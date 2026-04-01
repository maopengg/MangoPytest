# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 部门审批模块fixtures (C级)
# @Time   : 2026-03-31
# @Author : 毛鹏
import pytest

from auto_test.demo_project.data_factory.builders.dept_approval import (
    DeptApprovalBuilder,
)
from auto_test.demo_project.data_factory.builders.reimbursement import (
    ReimbursementBuilder,
)


@pytest.fixture
def dept_approval_builder(authenticated_client) -> DeptApprovalBuilder:
    """
    部门审批Builder Fixture
    提供DeptApprovalBuilder实例用于创建和管理部门审批数据

    使用示例:
        def test_example(dept_approval_builder, created_reimbursement):
            approval = dept_approval_builder.approve(created_reimbursement["id"])
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
    if hasattr(entity, '__dict__'):
        result = entity.__dict__.copy()
        result.pop('_is_new', None)
        result.pop('_is_deleted', None)
        return result
    return str(entity)


@pytest.fixture
def dept_approved_reimbursement(reimbursement_builder, dept_approval_builder) -> dict:
    """
    已通过部门审批的报销申请Fixture
    提供D级+C级完整数据

    使用示例:
        def test_with_dept_approval(dept_approved_reimbursement, dept_approval_builder):
            reimbursement = dept_approved_reimbursement["reimbursement"]
            approval = dept_approved_reimbursement["dept_approval"]
            assert reimbursement["status"] == "dept_approved"
    """
    # D级：创建报销申请
    reimbursement = reimbursement_builder.create(
        user_id=1, amount=1000.00, reason="部门审批测试"
    )

    # C级：部门审批通过
    dept_approval = dept_approval_builder.approve(reimbursement.id)

    return {"reimbursement": _entity_to_dict(reimbursement), "dept_approval": _entity_to_dict(dept_approval)}


@pytest.fixture
def dept_rejected_reimbursement(reimbursement_builder, dept_approval_builder) -> dict:
    """
    被部门拒绝的报销申请Fixture
    提供D级+C级(拒绝)完整数据
    """
    # D级：创建报销申请
    reimbursement = reimbursement_builder.create(
        user_id=1, amount=1000.00, reason="部门拒绝测试"
    )

    # C级：部门审批拒绝
    dept_approval = dept_approval_builder.reject(
        reimbursement.id, comment="不符合报销标准"
    )

    return {
        "reimbursement": _entity_to_dict(reimbursement),
        "dept_approval": _entity_to_dict(dept_approval),
        "status": "dept_rejected",
    }


@pytest.fixture
def dept_manager_id() -> int:
    """
    部门经理用户ID Fixture
    """
    return 3

# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 总经理审批模块fixtures (A级)
# @Time   : 2026-03-31
# @Author : 毛鹏
import pytest

from auto_test.demo_project.data_factory.builders.ceo_approval import CEOApprovalBuilder


@pytest.fixture
def ceo_approval_builder(api_client) -> CEOApprovalBuilder:
    """
    总经理审批Builder Fixture
    提供CEOApprovalBuilder实例用于创建和管理总经理审批数据

    使用示例:
        def test_example(ceo_approval_builder, finance_approved_reimbursement):
            approval = ceo_approval_builder.approve(
                finance_approved_reimbursement["reimbursement"]["id"],
                finance_approved_reimbursement["finance_approval"]["id"]
            )
            assert approval is not None
    """
    builder = CEOApprovalBuilder(token=api_client.token)
    yield builder
    # 清理创建的数据
    builder.cleanup()


@pytest.fixture
def fully_approved_reimbursement(reimbursement_builder, dept_approval_builder,
                                 finance_approval_builder, ceo_approval_builder) -> dict:
    """
    完全审批通过的报销申请Fixture
    提供D级+C级+B级+A级完整数据（完整4级审批流程）

    使用示例:
        def test_fully_approved(fully_approved_reimbursement):
            assert fully_approved_reimbursement["reimbursement"]["status"] == "ceo_approved"
            assert fully_approved_reimbursement["ceo_approval"] is not None
    """
    # D级：创建报销申请
    reimbursement = reimbursement_builder.create(
        user_id=1,
        amount=3000.00,
        reason="总经理审批测试"
    )

    # C级：部门审批通过
    dept_approval = dept_approval_builder.approve(reimbursement["id"])

    # B级：财务审批通过
    finance_approval = finance_approval_builder.approve(
        reimbursement["id"],
        dept_approval["id"]
    )

    # A级：总经理审批通过
    ceo_approval = ceo_approval_builder.approve(
        reimbursement["id"],
        finance_approval["id"]
    )

    return {
        "reimbursement": reimbursement,
        "dept_approval": dept_approval,
        "finance_approval": finance_approval,
        "ceo_approval": ceo_approval,
        "status": "ceo_approved"
    }


@pytest.fixture
def ceo_rejected_reimbursement(reimbursement_builder, dept_approval_builder,
                               finance_approval_builder, ceo_approval_builder) -> dict:
    """
    被总经理拒绝的报销申请Fixture
    提供D级+C级+B级+A级(拒绝)完整数据
    """
    # D级：创建报销申请
    reimbursement = reimbursement_builder.create(
        user_id=1,
        amount=10000.00,
        reason="总经理拒绝测试"
    )

    # C级：部门审批通过
    dept_approval = dept_approval_builder.approve(reimbursement["id"])

    # B级：财务审批通过
    finance_approval = finance_approval_builder.approve(
        reimbursement["id"],
        dept_approval["id"]
    )

    # A级：总经理审批拒绝
    ceo_approval = ceo_approval_builder.reject(
        reimbursement["id"],
        finance_approval["id"],
        comment="金额过大，不予批准"
    )

    return {
        "reimbursement": reimbursement,
        "dept_approval": dept_approval,
        "finance_approval": finance_approval,
        "ceo_approval": ceo_approval,
        "status": "ceo_rejected"
    }


@pytest.fixture
def ceo_id() -> int:
    """
    CEO用户ID Fixture
    """
    return 5


@pytest.fixture
def workflow_data(ceo_approval_builder, fully_approved_reimbursement) -> dict:
    """
    完整审批流程数据Fixture
    获取完整审批流程的详细信息
    """
    reimbursement_id = fully_approved_reimbursement["reimbursement"]["id"]
    return ceo_approval_builder.get_workflow(reimbursement_id)

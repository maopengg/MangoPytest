# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 财务审批模块fixtures (B级)
# @Time   : 2026-03-31
# @Author : 毛鹏
import pytest

from auto_test.demo_project.data_factory.builders.finance_approval import (
    FinanceApprovalBuilder,
)


@pytest.fixture
def finance_approval_builder(authenticated_client) -> FinanceApprovalBuilder:
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


@pytest.fixture
def finance_approved_reimbursement(
    reimbursement_builder, dept_approval_builder, finance_approval_builder
) -> dict:
    """
    已通过财务审批的报销申请Fixture
    提供D级+C级+B级完整数据
    """
    # D级：创建报销申请
    reimbursement = reimbursement_builder.create(
        user_id=1, amount=2000.00, reason="财务审批测试"
    )

    # C级：部门审批通过
    dept_approval = dept_approval_builder.approve(reimbursement["id"])

    # B级：财务审批通过
    finance_approval = finance_approval_builder.approve(
        reimbursement["id"], dept_approval["id"]
    )

    return {
        "reimbursement": reimbursement,
        "dept_approval": dept_approval,
        "finance_approval": finance_approval,
    }


@pytest.fixture
def finance_rejected_reimbursement(
    reimbursement_builder, dept_approval_builder, finance_approval_builder
) -> dict:
    """
    被财务拒绝的报销申请Fixture
    提供D级+C级+B级(拒绝)完整数据
    """
    # D级：创建报销申请
    reimbursement = reimbursement_builder.create(
        user_id=1, amount=5000.00, reason="财务拒绝测试"
    )

    # C级：部门审批通过
    dept_approval = dept_approval_builder.approve(reimbursement["id"])

    # B级：财务审批拒绝
    finance_approval = finance_approval_builder.reject(
        reimbursement["id"], dept_approval["id"], comment="金额超出预算"
    )

    return {
        "reimbursement": reimbursement,
        "dept_approval": dept_approval,
        "finance_approval": finance_approval,
        "status": "finance_rejected",
    }


@pytest.fixture
def finance_manager_id() -> int:
    """
    财务经理用户ID Fixture
    """
    return 4

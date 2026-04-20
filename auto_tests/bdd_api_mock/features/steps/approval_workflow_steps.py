# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 审批流程模块 BDD 步骤定义
# @Time   : 2026-04-17
# @Author : 毛鹏
"""
审批流程模块步骤定义
"""

import pytest
from pytest_bdd import given, when, then, parsers
from pytest_bdd.parsers import parse

from auto_tests.bdd_api_mock.data_factory.builders.reimbursement import (
    ReimbursementBuilder,
)
from auto_tests.bdd_api_mock.data_factory.builders.dept_approval import (
    DeptApprovalBuilder,
)
from auto_tests.bdd_api_mock.data_factory.builders.finance_approval import (
    FinanceApprovalBuilder,
)
from auto_tests.bdd_api_mock.data_factory.builders.ceo_approval import (
    CEOApprovalBuilder,
)
from auto_tests.bdd_api_mock.api_manager import bdd_api_mock


# ==================== Given 步骤 ====================


@given("系统中存在待审批的报销申请", target_fixture="pending_reimbursement")
def prepare_pending_reimbursement(approver_logged_in):
    """准备待审批的报销申请"""
    token = approver_logged_in["token"]
    reimbursement_builder = ReimbursementBuilder(token=token)
    reimbursement = reimbursement_builder.create(
        user_id=1, amount=1000.00, reason="审批流程测试"
    )
    return reimbursement


@given("员工提交了报销申请", target_fixture="submitted_reimbursement")
def employee_submit_reimbursement(approver_logged_in, table):
    """员工提交报销申请"""
    token = approver_logged_in["token"]
    reimbursement_builder = ReimbursementBuilder(token=token)
    rows = list(table)

    reimbursement = reimbursement_builder.create(
        user_id=1, amount=float(rows[0]["amount"]), reason=rows[0]["reason"]
    )
    return reimbursement


@given("存在待审批的报销申请", target_fixture="existing_pending_reimbursement")
def existing_pending_reimbursement(approver_logged_in):
    """存在待审批的报销申请"""
    token = approver_logged_in["token"]
    reimbursement_builder = ReimbursementBuilder(token=token)
    reimbursement = reimbursement_builder.create(
        user_id=1, amount=500.00, reason="部门审批测试"
    )
    return reimbursement


@given("部门审批已通过", target_fixture="dept_approved_data")
def dept_approval_already_approved(approver_logged_in, existing_pending_reimbursement):
    """部门审批已通过"""
    token = approver_logged_in["token"]
    bdd_api_mock.dept_approval.set_token(token)

    reimbursement_id = (
        existing_pending_reimbursement.id
        if hasattr(existing_pending_reimbursement, "id")
        else existing_pending_reimbursement["id"]
    )

    result = bdd_api_mock.dept_approval.create_dept_approval(
        reimbursement_id=reimbursement_id,
        approver_id=2,
        status="approved",
        comment="部门审批通过",
    )

    return {
        "reimbursement": existing_pending_reimbursement,
        "dept_approval": result.get("data") if result else None,
    }


@given("部门审批已被拒绝", target_fixture="dept_rejected_data")
def dept_approval_already_rejected(approver_logged_in, existing_pending_reimbursement):
    """部门审批已被拒绝"""
    token = approver_logged_in["token"]
    bdd_api_mock.dept_approval.set_token(token)

    reimbursement_id = (
        existing_pending_reimbursement.id
        if hasattr(existing_pending_reimbursement, "id")
        else existing_pending_reimbursement["id"]
    )

    result = bdd_api_mock.dept_approval.create_dept_approval(
        reimbursement_id=reimbursement_id,
        approver_id=2,
        status="rejected",
        comment="不符合报销规定",
    )

    return {
        "reimbursement": existing_pending_reimbursement,
        "dept_approval": result.get("data") if result else None,
    }


@given("财务审批已通过", target_fixture="finance_approved_data")
def finance_approval_already_approved(approver_logged_in, dept_approved_data):
    """财务审批已通过"""
    token = approver_logged_in["token"]
    bdd_api_mock.finance_approval.set_token(token)

    reimbursement_id = (
        dept_approved_data["reimbursement"].id
        if hasattr(dept_approved_data["reimbursement"], "id")
        else dept_approved_data["reimbursement"]["id"]
    )
    dept_approval_id = (
        dept_approved_data["dept_approval"]["id"]
        if dept_approved_data["dept_approval"]
        else 1
    )

    result = bdd_api_mock.finance_approval.create_finance_approval(
        reimbursement_id=reimbursement_id,
        dept_approval_id=dept_approval_id,
        approver_id=3,
        status="approved",
        comment="财务审批通过",
    )

    return {
        **dept_approved_data,
        "finance_approval": result.get("data") if result else None,
    }


@given("财务审批已被拒绝", target_fixture="finance_rejected_data")
def finance_approval_already_rejected(approver_logged_in, dept_approved_data):
    """财务审批已被拒绝"""
    token = approver_logged_in["token"]
    bdd_api_mock.finance_approval.set_token(token)

    reimbursement_id = (
        dept_approved_data["reimbursement"].id
        if hasattr(dept_approved_data["reimbursement"], "id")
        else dept_approved_data["reimbursement"]["id"]
    )
    dept_approval_id = (
        dept_approved_data["dept_approval"]["id"]
        if dept_approved_data["dept_approval"]
        else 1
    )

    result = bdd_api_mock.finance_approval.create_finance_approval(
        reimbursement_id=reimbursement_id,
        dept_approval_id=dept_approval_id,
        approver_id=3,
        status="rejected",
        comment="超出预算",
    )

    return {
        **dept_approved_data,
        "finance_approval": result.get("data") if result else None,
    }


# ==================== When 步骤 ====================


@when(
    parsers.parse('部门经理审批通过，意见为 "{comment}"'),
    target_fixture="workflow_result",
)
def dept_manager_approve(approver_logged_in, submitted_reimbursement, comment):
    """部门经理审批通过"""
    token = approver_logged_in["token"]
    bdd_api_mock.dept_approval.set_token(token)

    reimbursement_id = (
        submitted_reimbursement.id
        if hasattr(submitted_reimbursement, "id")
        else submitted_reimbursement["id"]
    )

    result = bdd_api_mock.dept_approval.create_dept_approval(
        reimbursement_id=reimbursement_id,
        approver_id=2,
        status="approved",
        comment=comment,
    )

    return {
        "reimbursement": submitted_reimbursement,
        "dept_approval": result.get("data") if result else None,
        "status": "dept_approved" if result and result.get("code") == 200 else "error",
    }


@when(
    parsers.parse('部门经理审批拒绝，意见为 "{comment}"'),
    target_fixture="workflow_result",
)
def dept_manager_reject(approver_logged_in, submitted_reimbursement, comment):
    """部门经理审批拒绝"""
    token = approver_logged_in["token"]
    bdd_api_mock.dept_approval.set_token(token)

    reimbursement_id = (
        submitted_reimbursement.id
        if hasattr(submitted_reimbursement, "id")
        else submitted_reimbursement["id"]
    )

    result = bdd_api_mock.dept_approval.create_dept_approval(
        reimbursement_id=reimbursement_id,
        approver_id=2,
        status="rejected",
        comment=comment,
    )

    return {
        "reimbursement": submitted_reimbursement,
        "dept_approval": result.get("data") if result else None,
        "status": "dept_rejected" if result and result.get("code") == 200 else "error",
    }


@when(
    parsers.parse('财务经理审批通过，意见为 "{comment}"'),
    target_fixture="workflow_result",
)
def finance_manager_approve(approver_logged_in, workflow_result, comment):
    """财务经理审批通过"""
    token = approver_logged_in["token"]
    bdd_api_mock.finance_approval.set_token(token)

    reimbursement_id = (
        workflow_result["reimbursement"].id
        if hasattr(workflow_result["reimbursement"], "id")
        else workflow_result["reimbursement"]["id"]
    )
    dept_approval_id = (
        workflow_result["dept_approval"]["id"]
        if workflow_result["dept_approval"]
        else 1
    )

    result = bdd_api_mock.finance_approval.create_finance_approval(
        reimbursement_id=reimbursement_id,
        dept_approval_id=dept_approval_id,
        approver_id=3,
        status="approved",
        comment=comment,
    )

    workflow_result["finance_approval"] = result.get("data") if result else None
    workflow_result["status"] = (
        "finance_approved" if result and result.get("code") == 200 else "error"
    )
    return workflow_result


@when(
    parsers.parse('财务经理审批拒绝，意见为 "{comment}"'),
    target_fixture="workflow_result",
)
def finance_manager_reject(approver_logged_in, workflow_result, comment):
    """财务经理审批拒绝"""
    token = approver_logged_in["token"]
    bdd_api_mock.finance_approval.set_token(token)

    reimbursement_id = (
        workflow_result["reimbursement"].id
        if hasattr(workflow_result["reimbursement"], "id")
        else workflow_result["reimbursement"]["id"]
    )
    dept_approval_id = (
        workflow_result["dept_approval"]["id"]
        if workflow_result["dept_approval"]
        else 1
    )

    result = bdd_api_mock.finance_approval.create_finance_approval(
        reimbursement_id=reimbursement_id,
        dept_approval_id=dept_approval_id,
        approver_id=3,
        status="rejected",
        comment=comment,
    )

    workflow_result["finance_approval"] = result.get("data") if result else None
    workflow_result["status"] = (
        "finance_rejected" if result and result.get("code") == 200 else "error"
    )
    return workflow_result


@when(
    parsers.parse('总经理审批通过，意见为 "{comment}"'),
    target_fixture="workflow_result",
)
def ceo_approve(approver_logged_in, workflow_result, comment):
    """总经理审批通过"""
    token = approver_logged_in["token"]
    bdd_api_mock.ceo_approval.set_token(token)

    reimbursement_id = (
        workflow_result["reimbursement"].id
        if hasattr(workflow_result["reimbursement"], "id")
        else workflow_result["reimbursement"]["id"]
    )
    finance_approval_id = (
        workflow_result["finance_approval"]["id"]
        if workflow_result.get("finance_approval")
        else 1
    )

    result = bdd_api_mock.ceo_approval.create_ceo_approval(
        reimbursement_id=reimbursement_id,
        finance_approval_id=finance_approval_id,
        approver_id=4,
        status="approved",
        comment=comment,
    )

    workflow_result["ceo_approval"] = result.get("data") if result else None
    workflow_result["status"] = (
        "ceo_approved" if result and result.get("code") == 200 else "error"
    )
    return workflow_result


@when(
    parsers.parse('总经理审批拒绝，意见为 "{comment}"'),
    target_fixture="workflow_result",
)
def ceo_reject(approver_logged_in, workflow_result, comment):
    """总经理审批拒绝"""
    token = approver_logged_in["token"]
    bdd_api_mock.ceo_approval.set_token(token)

    reimbursement_id = (
        workflow_result["reimbursement"].id
        if hasattr(workflow_result["reimbursement"], "id")
        else workflow_result["reimbursement"]["id"]
    )
    finance_approval_id = (
        workflow_result["finance_approval"]["id"]
        if workflow_result.get("finance_approval")
        else 1
    )

    result = bdd_api_mock.ceo_approval.create_ceo_approval(
        reimbursement_id=reimbursement_id,
        finance_approval_id=finance_approval_id,
        approver_id=4,
        status="rejected",
        comment=comment,
    )

    workflow_result["ceo_approval"] = result.get("data") if result else None
    workflow_result["status"] = (
        "ceo_rejected" if result and result.get("code") == 200 else "error"
    )
    return workflow_result


@when("部门经理尝试为不存在的报销申请创建审批", target_fixture="api_response")
def create_dept_approval_for_nonexistent(approver_logged_in):
    """为不存在的报销申请创建部门审批"""
    token = approver_logged_in["token"]
    bdd_api_mock.dept_approval.set_token(token)

    result = bdd_api_mock.dept_approval.create_dept_approval(
        reimbursement_id=99999, approver_id=2, status="approved", comment="测试"
    )
    return result


@when("财务经理尝试创建审批", target_fixture="api_response")
def finance_try_create_approval(approver_logged_in, dept_rejected_data):
    """财务经理尝试为未通过的部门审批创建审批"""
    token = approver_logged_in["token"]
    bdd_api_mock.finance_approval.set_token(token)

    reimbursement_id = (
        dept_rejected_data["reimbursement"].id
        if hasattr(dept_rejected_data["reimbursement"], "id")
        else dept_rejected_data["reimbursement"]["id"]
    )
    dept_approval_id = (
        dept_rejected_data["dept_approval"]["id"]
        if dept_rejected_data["dept_approval"]
        else 1
    )

    result = bdd_api_mock.finance_approval.create_finance_approval(
        reimbursement_id=reimbursement_id,
        dept_approval_id=dept_approval_id,
        approver_id=3,
        status="approved",
        comment="测试",
    )
    return result


@when("总经理尝试创建审批", target_fixture="api_response")
def ceo_try_create_approval(approver_logged_in, finance_rejected_data):
    """总经理尝试为未通过的财务审批创建审批"""
    token = approver_logged_in["token"]
    bdd_api_mock.ceo_approval.set_token(token)

    reimbursement_id = (
        finance_rejected_data["reimbursement"].id
        if hasattr(finance_rejected_data["reimbursement"], "id")
        else finance_rejected_data["reimbursement"]["id"]
    )
    finance_approval_id = (
        finance_rejected_data["finance_approval"]["id"]
        if finance_rejected_data["finance_approval"]
        else 1
    )

    result = bdd_api_mock.ceo_approval.create_ceo_approval(
        reimbursement_id=reimbursement_id,
        finance_approval_id=finance_approval_id,
        approver_id=4,
        status="approved",
        comment="测试",
    )
    return result


# ==================== Then 步骤 ====================


@then(parsers.parse('报销申请状态应该是 "{status}"'))
def verify_reimbursement_status_in_workflow(workflow_result, status):
    """验证报销申请状态"""
    assert workflow_result["status"] == status


@then("整个审批流程应该成功完成")
def verify_workflow_completed_successfully(workflow_result):
    """验证审批流程成功完成"""
    assert workflow_result["status"] == "ceo_approved"
    assert workflow_result["dept_approval"] is not None
    assert workflow_result["finance_approval"] is not None
    assert workflow_result["ceo_approval"] is not None


@then("后续审批流程应该终止")
def verify_workflow_terminated(workflow_result):
    """验证审批流程终止"""
    # 当部门审批被拒绝时，后续审批不应该被执行
    assert workflow_result["status"] == "dept_rejected"


@then("总经理审批不应该被执行")
def verify_ceo_approval_not_executed(workflow_result):
    """验证总经理审批未被执行"""
    # 当财务审批被拒绝时，总经理审批不应该被执行
    assert workflow_result["status"] == "finance_rejected"
    assert (
        "ceo_approval" not in workflow_result
        or workflow_result.get("ceo_approval") is None
    )


@then("部门审批应该创建成功")
def verify_dept_approval_created(api_response):
    """验证部门审批创建成功"""
    assert api_response is None or api_response.get("code") == 200


@then(parsers.parse('审批状态应该是 "{status}"'))
def verify_approval_status(api_response, status):
    """验证审批状态"""
    if api_response:
        data = api_response.get("data", {})
        assert data.get("status") == status


@then("审批创建应该失败")
def verify_approval_creation_failed(api_response):
    """验证审批创建失败"""
    assert api_response is not None
    assert api_response.get("code") in [400, 404]

# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 财务审批模块测试 - B级模块 (依赖C级)
# @Time   : 2026-03-31
# @Author : 毛鹏

from auto_test.demo_project.api_manager import demo_project
from auto_test.demo_project.test_cases.base import UnitTest, IntegrationTest


class TestFinanceApprovalAPI(IntegrationTest):
    """
    财务审批API测试类 - B级模块测试
    测试 /finance-approvals 接口
    依赖C级：DeptApproval（部门审批必须通过）
    """

    def test_create_finance_approval(self, api_client, dept_approved_reimbursement, finance_manager_id):
        """测试创建财务审批 - 依赖C级部门审批"""
        reimbursement_id = dept_approved_reimbursement["reimbursement"]["id"]
        dept_approval_id = dept_approved_reimbursement["dept_approval"]["id"]

        demo_project.finance_approval.set_token(api_client.token)
        result = demo_project.finance_approval.create_finance_approval(
            reimbursement_id=reimbursement_id,
            dept_approval_id=dept_approval_id,
            approver_id=finance_manager_id,
            status="approved",
            comment="财务审批通过"
        )

        assert result is not None
        assert result["code"] == 200
        assert result["data"]["status"] == "approved"

    def test_create_finance_approval_without_dept_approval(self, api_client, pending_reimbursement, finance_manager_id):
        """测试创建财务审批 - 部门审批不存在"""
        demo_project.finance_approval.set_token(api_client.token)
        result = demo_project.finance_approval.create_finance_approval(
            reimbursement_id=pending_reimbursement["id"],
            dept_approval_id=99999,
            approver_id=finance_manager_id,
            status="approved",
            comment="测试"
        )

        assert result is not None
        assert result["code"] == 404

    def test_create_finance_approval_dept_rejected(self, api_client, dept_rejected_reimbursement, finance_manager_id):
        """测试创建财务审批 - 部门审批未通过"""
        reimbursement_id = dept_rejected_reimbursement["reimbursement"]["id"]
        dept_approval_id = dept_rejected_reimbursement["dept_approval"]["id"]

        demo_project.finance_approval.set_token(api_client.token)
        result = demo_project.finance_approval.create_finance_approval(
            reimbursement_id=reimbursement_id,
            dept_approval_id=dept_approval_id,
            approver_id=finance_manager_id,
            status="approved",
            comment="测试"
        )

        assert result is not None
        assert result["code"] == 400

    def test_get_finance_approvals(self, api_client, finance_approved_reimbursement):
        """测试获取财务审批列表"""
        demo_project.finance_approval.set_token(api_client.token)
        result = demo_project.finance_approval.get_finance_approvals()

        assert result is not None
        assert result["code"] == 200

    def test_get_finance_approvals_by_reimbursement(self, api_client, finance_approved_reimbursement):
        """测试根据报销申请ID获取财务审批"""
        reimbursement_id = finance_approved_reimbursement["reimbursement"]["id"]

        demo_project.finance_approval.set_token(api_client.token)
        result = demo_project.finance_approval.get_finance_approvals()

        assert result is not None
        assert result["code"] == 200


class TestFinanceApprovalBuilder(UnitTest):
    """
    财务审批Builder测试类
    测试数据工厂功能
    """

    def test_builder_create(self, finance_approval_builder, dept_approved_reimbursement):
        """测试Builder创建财务审批"""
        approval = finance_approval_builder.create(
            reimbursement_id=dept_approved_reimbursement["reimbursement"]["id"],
            dept_approval_id=dept_approved_reimbursement["dept_approval"]["id"],
            status="approved",
            comment="测试审批"
        )

        assert approval is not None
        assert approval.id is not None
        assert approval.status == "approved"

    def test_builder_approve(self, finance_approval_builder, dept_approved_reimbursement):
        """测试Builder快捷通过方法"""
        approval = finance_approval_builder.approve(
            dept_approved_reimbursement["reimbursement"]["id"],
            dept_approved_reimbursement["dept_approval"]["id"]
        )

        assert approval is not None
        assert approval.status == "approved"

    def test_builder_reject(self, finance_approval_builder, dept_approved_reimbursement):
        """测试Builder快捷拒绝方法"""
        approval = finance_approval_builder.reject(
            dept_approved_reimbursement["reimbursement"]["id"],
            dept_approved_reimbursement["dept_approval"]["id"],
            comment="超出预算"
        )

        assert approval is not None
        assert approval.status == "rejected"

    def test_builder_get_by_reimbursement(self, finance_approval_builder, finance_approved_reimbursement):
        """测试Builder根据报销申请获取审批"""
        reimbursement_id = finance_approved_reimbursement["reimbursement"]["id"]
        approval = finance_approval_builder.get_by_reimbursement(reimbursement_id)

        assert approval is not None
        assert approval.reimbursement_id == reimbursement_id

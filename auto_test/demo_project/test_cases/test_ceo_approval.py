# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 总经理审批模块测试 - A级模块 (依赖B级)
# @Time   : 2026-03-31
# @Author : 毛鹏
import pytest

from auto_test.demo_project.api_manager import demo_project
from auto_test.demo_project.fixtures.conftest import *
from auto_test.demo_project.test_cases.base import UnitTest, IntegrationTest


class TestCEOApprovalAPI(IntegrationTest):
    """
    总经理审批API测试类 - A级模块测试
    测试 /ceo-approvals 接口
    依赖B级：FinanceApproval（财务审批必须通过）
    """

    def test_create_ceo_approval(
        self, api_client, finance_approved_reimbursement, ceo_id
    ):
        """测试创建总经理审批 - 依赖B级财务审批"""
        reimbursement_id = finance_approved_reimbursement["reimbursement"]["id"]
        finance_approval_id = finance_approved_reimbursement["finance_approval"]["id"]

        demo_project.ceo_approval.set_token(api_client.token)
        result = demo_project.ceo_approval.create_ceo_approval(
            reimbursement_id=reimbursement_id,
            finance_approval_id=finance_approval_id,
            approver_id=ceo_id,
            status="approved",
            comment="总经理审批通过",
        )

        assert result is not None
        assert result["code"] == 200
        assert result["data"]["status"] == "approved"

    def test_create_ceo_approval_without_finance_approval(
        self, api_client, dept_approved_reimbursement, ceo_id
    ):
        """测试创建总经理审批 - 财务审批不存在"""
        demo_project.ceo_approval.set_token(api_client.token)
        result = demo_project.ceo_approval.create_ceo_approval(
            reimbursement_id=dept_approved_reimbursement["reimbursement"]["id"],
            finance_approval_id=99999,
            approver_id=ceo_id,
            status="approved",
            comment="测试",
        )

        assert result is not None
        assert result["code"] == 404

    def test_create_ceo_approval_finance_rejected(
        self, api_client, finance_rejected_reimbursement, ceo_id
    ):
        """测试创建总经理审批 - 财务审批未通过"""
        reimbursement_id = finance_rejected_reimbursement["reimbursement"]["id"]
        finance_approval_id = finance_rejected_reimbursement["finance_approval"]["id"]

        demo_project.ceo_approval.set_token(api_client.token)
        result = demo_project.ceo_approval.create_ceo_approval(
            reimbursement_id=reimbursement_id,
            finance_approval_id=finance_approval_id,
            approver_id=ceo_id,
            status="approved",
            comment="测试",
        )

        assert result is not None
        assert result["code"] == 400

    def test_get_ceo_approvals(self, api_client, fully_approved_reimbursement):
        """测试获取总经理审批列表"""
        # 使用全局token设置
        if hasattr(api_client, "token") and api_client.token:
            demo_project.auth.set_token(api_client.token)
        result = demo_project.ceo_approval.get_ceo_approvals()

        assert result is not None
        assert result["code"] == 200

    def test_get_ceo_approvals_by_reimbursement(
        self, api_client, fully_approved_reimbursement
    ):
        """测试根据报销申请ID获取总经理审批"""
        reimbursement_id = fully_approved_reimbursement["reimbursement"]["id"]

        # 使用全局token设置
        if hasattr(api_client, "token") and api_client.token:
            demo_project.auth.set_token(api_client.token)
        result = demo_project.ceo_approval.get_ceo_approval_by_id(
            approval_id=reimbursement_id
        )

        assert result is not None
        assert result["code"] == 200


class TestCEOApprovalBuilder(UnitTest):
    """
    总经理审批Builder测试类
    测试数据工厂功能
    """

    def test_builder_create(self, ceo_approval_builder, finance_approved_reimbursement):
        """测试Builder创建总经理审批"""
        approval = ceo_approval_builder.create(
            reimbursement_id=finance_approved_reimbursement["reimbursement"]["id"],
            finance_approval_id=finance_approved_reimbursement["finance_approval"][
                "id"
            ],
            status="approved",
            comment="测试审批",
        )

        assert approval is not None
        assert approval.id is not None
        assert approval.status == "approved"

    def test_builder_approve(
        self, ceo_approval_builder, finance_approved_reimbursement
    ):
        """测试Builder快捷通过方法"""
        approval = ceo_approval_builder.approve(
            finance_approved_reimbursement["reimbursement"]["id"],
            finance_approved_reimbursement["finance_approval"]["id"],
        )

        assert approval is not None
        assert approval.status == "approved"

    def test_builder_reject(self, ceo_approval_builder, finance_approved_reimbursement):
        """测试Builder快捷拒绝方法"""
        approval = ceo_approval_builder.reject(
            finance_approved_reimbursement["reimbursement"]["id"],
            finance_approved_reimbursement["finance_approval"]["id"],
            comment="金额过大",
        )

        assert approval is not None
        assert approval.status == "rejected"

    def test_builder_get_by_reimbursement(
        self, ceo_approval_builder, fully_approved_reimbursement
    ):
        """测试Builder根据报销申请获取审批"""
        reimbursement_id = fully_approved_reimbursement["reimbursement"]["id"]
        approval = ceo_approval_builder.get_by_reimbursement(reimbursement_id)

        assert approval is not None
        assert approval.reimbursement_id == reimbursement_id

    def test_builder_get_workflow(
        self, ceo_approval_builder, fully_approved_reimbursement
    ):
        """测试Builder获取完整审批流程"""
        reimbursement_id = fully_approved_reimbursement["reimbursement"]["id"]
        workflow = ceo_approval_builder.get_workflow(reimbursement_id)

        assert workflow is not None
        assert workflow["reimbursement"]["id"] == reimbursement_id
        assert workflow["dept_approval"] is not None
        assert workflow["finance_approval"] is not None
        assert workflow["ceo_approval"] is not None

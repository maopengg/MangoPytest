# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 审批流集成测试 - 4级审批依赖完整流程测试
# @Time   : 2026-03-31
# @Author : 毛鹏
import pytest

from auto_test.demo_project.api_manager import demo_project
from auto_test.demo_project.fixtures.conftest import *
from models.api_model import ApiDataModel, RequestModel


class TestApprovalWorkflow:
    """
    审批流集成测试类
    测试4级审批依赖的完整流程：
    D级：Reimbursement -> C级：DeptApproval -> B级：FinanceApproval -> A级：CEOApproval
    """

    def test_full_approval_workflow(self, api_client, approval_scenarios):
        """测试完整的4级审批流程 - 全部通过"""
        workflow = approval_scenarios.create_full_approval_workflow(
            user_id=1,
            amount=5000.00,
            reason="完整流程测试",
            approved=True
        )

        assert workflow["status"] == "fully_approved"
        assert workflow["reimbursement"] is not None
        assert workflow["dept_approval"] is not None
        assert workflow["finance_approval"] is not None
        assert workflow["ceo_approval"] is not None

        # 验证最终状态
        reimbursement = workflow["reimbursement"]
        assert reimbursement["status"] == "ceo_approved"

    def test_dept_rejection_workflow(self, api_client, approval_scenarios):
        """测试部门审批拒绝流程"""
        workflow = approval_scenarios.create_dept_rejected_workflow(
            user_id=1,
            amount=1000.00,
            reason="部门拒绝测试",
            comment="不符合报销规定"
        )

        assert workflow["status"] == "dept_rejected"
        assert workflow["reimbursement"] is not None
        assert workflow["dept_approval"] is not None
        assert workflow["dept_approval"]["status"] == "rejected"

    def test_finance_rejection_workflow(self, api_client, approval_scenarios):
        """测试财务审批拒绝流程"""
        workflow = approval_scenarios.create_finance_rejected_workflow(
            user_id=1,
            amount=8000.00,
            reason="财务拒绝测试",
            comment="超出预算"
        )

        assert workflow["status"] == "finance_rejected"
        assert workflow["reimbursement"] is not None
        assert workflow["dept_approval"] is not None
        assert workflow["finance_approval"] is not None
        assert workflow["finance_approval"]["status"] == "rejected"

    def test_ceo_rejection_workflow(self, api_client, approval_scenarios):
        """测试总经理审批拒绝流程"""
        workflow = approval_scenarios.create_ceo_rejected_workflow(
            user_id=1,
            amount=50000.00,
            reason="总经理拒绝测试",
            comment="金额过大"
        )

        assert workflow["status"] == "ceo_rejected"
        assert workflow["reimbursement"] is not None
        assert workflow["dept_approval"] is not None
        assert workflow["finance_approval"] is not None
        assert workflow["ceo_approval"] is not None
        assert workflow["ceo_approval"]["status"] == "rejected"

    def test_workflow_status_transitions(self, api_client, approval_scenarios):
        """测试审批流程状态流转"""
        # 创建待部门审批状态
        pending_dept = approval_scenarios.create_pending_at_dept(
            user_id=1,
            amount=1000.00,
            reason="状态流转测试"
        )
        assert pending_dept["status"] == "pending_at_dept"
        assert pending_dept["reimbursement"]["status"] == "pending"

        reimbursement_id = pending_dept["reimbursement"]["id"]

        # 推进到待财务审批
        pending_finance = approval_scenarios.create_pending_at_finance(
            user_id=1,
            amount=1000.00,
            reason="状态流转测试"
        )
        assert pending_finance["status"] == "pending_at_finance"
        assert pending_finance["reimbursement"]["status"] == "dept_approved"

        # 推进到待总经理审批
        pending_ceo = approval_scenarios.create_pending_at_ceo(
            user_id=1,
            amount=1000.00,
            reason="状态流转测试"
        )
        assert pending_ceo["status"] == "pending_at_ceo"
        assert pending_ceo["reimbursement"]["status"] == "finance_approved"

    def test_workflow_dependencies(self, api_client, approval_scenarios):
        """测试审批流程依赖关系"""
        # 创建完整流程
        workflow = approval_scenarios.create_full_approval_workflow()

        # 验证依赖关系
        reimbursement_id = workflow["reimbursement"]["id"]
        dept_approval_id = workflow["dept_approval"]["id"]
        finance_approval_id = workflow["finance_approval"]["id"]
        ceo_approval_id = workflow["ceo_approval"]["id"]

        # C级依赖D级
        assert workflow["dept_approval"]["reimbursement_id"] == reimbursement_id

        # B级依赖C级
        assert workflow["finance_approval"]["reimbursement_id"] == reimbursement_id
        assert workflow["finance_approval"]["dept_approval_id"] == dept_approval_id

        # A级依赖B级
        assert workflow["ceo_approval"]["reimbursement_id"] == reimbursement_id
        assert workflow["ceo_approval"]["finance_approval_id"] == finance_approval_id

    def test_get_full_workflow(self, api_client, fully_approved_reimbursement, ceo_approval_builder):
        """测试获取完整审批流程信息"""
        reimbursement_id = fully_approved_reimbursement["reimbursement"]["id"]

        workflow = ceo_approval_builder.get_workflow(reimbursement_id)

        assert workflow is not None
        assert workflow["reimbursement"]["id"] == reimbursement_id
        assert workflow["dept_approval"]["reimbursement_id"] == reimbursement_id
        assert workflow["finance_approval"]["reimbursement_id"] == reimbursement_id
        assert workflow["ceo_approval"]["reimbursement_id"] == reimbursement_id


class TestApprovalScenarios:
    """
    审批流场景测试类
    使用场景fixtures进行测试
    """

    def test_full_approval_workflow_scenario(self, full_approval_workflow):
        """测试完整审批通过场景"""
        assert full_approval_workflow["status"] == "fully_approved"
        assert full_approval_workflow["reimbursement"]["status"] == "ceo_approved"

    def test_dept_rejected_scenario(self, dept_rejected_workflow):
        """测试部门拒绝场景"""
        assert dept_rejected_workflow["status"] == "dept_rejected"
        assert dept_rejected_workflow["dept_approval"]["status"] == "rejected"

    def test_finance_rejected_scenario(self, finance_rejected_workflow):
        """测试财务拒绝场景"""
        assert finance_rejected_workflow["status"] == "finance_rejected"
        assert finance_rejected_workflow["finance_approval"]["status"] == "rejected"

    def test_ceo_rejected_scenario(self, ceo_rejected_workflow):
        """测试总经理拒绝场景"""
        assert ceo_rejected_workflow["status"] == "ceo_rejected"
        assert ceo_rejected_workflow["ceo_approval"]["status"] == "rejected"

    def test_pending_at_dept_scenario(self, pending_at_dept):
        """测试待部门审批场景"""
        assert pending_at_dept["status"] == "pending_at_dept"
        assert pending_at_dept["reimbursement"]["status"] == "pending"

    def test_pending_at_finance_scenario(self, pending_at_finance):
        """测试待财务审批场景"""
        assert pending_at_finance["status"] == "pending_at_finance"
        assert pending_at_finance["reimbursement"]["status"] == "dept_approved"

    def test_pending_at_ceo_scenario(self, pending_at_ceo):
        """测试待总经理审批场景"""
        assert pending_at_ceo["status"] == "pending_at_ceo"
        assert pending_at_ceo["reimbursement"]["status"] == "finance_approved"

    def test_multi_level_workflows(self, multi_level_workflows):
        """测试多级审批流程集合"""
        assert len(multi_level_workflows) == 4

        statuses = [w["status"] for w in multi_level_workflows]
        assert "fully_approved" in statuses
        assert "dept_rejected" in statuses
        assert "finance_rejected" in statuses
        assert "ceo_rejected" in statuses


class TestApprovalDependencyValidation:
    """
    审批依赖验证测试类
    验证框架的依赖管理是否正确
    """

    def test_cannot_skip_dept_approval(self, api_client, pending_reimbursement,
                                       finance_manager_id, ceo_id):
        """测试不能跳过部门审批直接进行财务审批"""
        # 尝试直接进行财务审批（没有部门审批）
        api_data = ApiDataModel(
            request=RequestModel(
                url="/finance-approvals",
                method="POST",
                headers={"Authorization": f"Bearer {api_client.token}"},
                json_data={
                    "reimbursement_id": pending_reimbursement["id"],
                    "dept_approval_id": 99999,  # 不存在的部门审批
                    "approver_id": finance_manager_id,
                    "status": "approved",
                    "comment": "测试"
                }
            )
        )

        result = demo_project.finance_approval.create_finance_approval(api_data)
        assert result.response.json()["code"] == 404

    def test_cannot_skip_finance_approval(self, api_client, dept_approved_reimbursement, ceo_id):
        """测试不能跳过财务审批直接进行总经理审批"""
        # 尝试直接进行总经理审批（没有财务审批）
        api_data = ApiDataModel(
            request=RequestModel(
                url="/ceo-approvals",
                method="POST",
                headers={"Authorization": f"Bearer {api_client.token}"},
                json_data={
                    "reimbursement_id": dept_approved_reimbursement["reimbursement"]["id"],
                    "finance_approval_id": 99999,  # 不存在的财务审批
                    "approver_id": ceo_id,
                    "status": "approved",
                    "comment": "测试"
                }
            )
        )

        result = demo_project.ceo_approval.create_ceo_approval(api_data)
        assert result.response.json()["code"] == 404

    def test_dept_rejected_cannot_proceed(self, api_client, dept_rejected_reimbursement,
                                          finance_manager_id):
        """测试部门拒绝后不能进行财务审批"""
        dept_approval_id = dept_rejected_reimbursement["dept_approval"]["id"]

        api_data = ApiDataModel(
            request=RequestModel(
                url="/finance-approvals",
                method="POST",
                headers={"Authorization": f"Bearer {api_client.token}"},
                json_data={
                    "reimbursement_id": dept_rejected_reimbursement["reimbursement"]["id"],
                    "dept_approval_id": dept_approval_id,
                    "approver_id": finance_manager_id,
                    "status": "approved",
                    "comment": "测试"
                }
            )
        )

        result = demo_project.finance_approval.create_finance_approval(api_data)
        assert result.response.json()["code"] == 400

    def test_finance_rejected_cannot_proceed(self, api_client, finance_rejected_reimbursement, ceo_id):
        """测试财务拒绝后不能进行总经理审批"""
        finance_approval_id = finance_rejected_reimbursement["finance_approval"]["id"]

        api_data = ApiDataModel(
            request=RequestModel(
                url="/ceo-approvals",
                method="POST",
                headers={"Authorization": f"Bearer {api_client.token}"},
                json_data={
                    "reimbursement_id": finance_rejected_reimbursement["reimbursement"]["id"],
                    "finance_approval_id": finance_approval_id,
                    "approver_id": ceo_id,
                    "status": "approved",
                    "comment": "测试"
                }
            )
        )

        result = demo_project.ceo_approval.create_ceo_approval(api_data)
        assert result.response.json()["code"] == 400

# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 审批流集成测试 - 新架构版本
# @Time   : 2026-04-01
# @Author : 毛鹏
"""
审批流集成测试 - 使用新架构特性：
- E2ETest 端到端测试层
- 场景 Fixtures (full_approval_workflow, dept_rejected_workflow)
- test_context 上下文管理
- 依赖验证
"""

import pytest
import allure

from auto_test.demo_project.test_cases.base import IntegrationTest, E2ETest
from auto_test.demo_project.fixtures.conftest import *
from auto_test.demo_project.api_manager import demo_project


@allure.feature("审批流")
@allure.story("完整审批流程")
class TestFullApprovalWorkflow(E2ETest):
    """完整审批流程测试 - E2E层"""

    @allure.title("完整4级审批流程 - 全部通过")
    def test_full_approval_workflow_success(
        self, api_client, approval_scenarios, test_context
    ):
        """测试完整的4级审批流程 - 全部通过"""
        workflow = approval_scenarios.create_full_approval_workflow(
            user_id=1, amount=5000.00, reason="完整流程测试", approved=True
        )

        assert workflow["status"] == "fully_approved"
        assert workflow["reimbursement"] is not None
        assert workflow["dept_approval"] is not None
        assert workflow["finance_approval"] is not None
        assert workflow["ceo_approval"] is not None

        # 验证最终状态
        reimbursement = workflow["reimbursement"]
        assert reimbursement["status"] == "ceo_approved"

        test_context.set("workflow", workflow)

    @allure.title("完整审批流程 - 使用Fixture")
    def test_full_approval_with_fixture(self, full_approval_workflow, test_context):
        """测试使用full_approval_workflow fixture"""
        assert full_approval_workflow["status"] == "fully_approved"
        assert full_approval_workflow["reimbursement"]["status"] == "ceo_approved"

        test_context.set("workflow", full_approval_workflow)

    @allure.title("部门审批拒绝流程")
    def test_dept_rejection_workflow(
        self, api_client, approval_scenarios, test_context
    ):
        """测试部门审批拒绝流程"""
        workflow = approval_scenarios.create_dept_rejected_workflow(
            user_id=1, amount=1000.00, reason="部门拒绝测试", comment="不符合报销规定"
        )

        assert workflow["status"] == "dept_rejected"
        assert workflow["reimbursement"] is not None
        assert workflow["dept_approval"] is not None
        assert workflow["dept_approval"]["status"] == "rejected"

        test_context.set("workflow", workflow)

    @allure.title("财务审批拒绝流程")
    def test_finance_rejection_workflow(
        self, api_client, approval_scenarios, test_context
    ):
        """测试财务审批拒绝流程"""
        workflow = approval_scenarios.create_finance_rejected_workflow(
            user_id=1, amount=8000.00, reason="财务拒绝测试", comment="超出预算"
        )

        assert workflow["status"] == "finance_rejected"
        assert workflow["reimbursement"] is not None
        assert workflow["dept_approval"] is not None
        assert workflow["finance_approval"] is not None
        assert workflow["finance_approval"]["status"] == "rejected"

        test_context.set("workflow", workflow)

    @allure.title("总经理审批拒绝流程")
    def test_ceo_rejection_workflow(self, api_client, approval_scenarios, test_context):
        """测试总经理审批拒绝流程"""
        workflow = approval_scenarios.create_ceo_rejected_workflow(
            user_id=1, amount=50000.00, reason="总经理拒绝测试", comment="金额过大"
        )

        assert workflow["status"] == "ceo_rejected"
        assert workflow["reimbursement"] is not None
        assert workflow["dept_approval"] is not None
        assert workflow["finance_approval"] is not None
        assert workflow["ceo_approval"] is not None
        assert workflow["ceo_approval"]["status"] == "rejected"

        test_context.set("workflow", workflow)


@allure.feature("审批流")
@allure.story("审批状态流转")
class TestApprovalStatusTransitions(IntegrationTest):
    """审批状态流转测试"""

    @allure.title("审批流程状态流转")
    def test_workflow_status_transitions(self, api_client, approval_scenarios):
        """测试审批流程状态流转"""
        # 创建待部门审批状态
        pending_dept = approval_scenarios.create_pending_at_dept(
            user_id=1, amount=1000.00, reason="状态流转测试"
        )
        assert pending_dept["status"] == "pending_at_dept"
        assert pending_dept["reimbursement"]["status"] == "pending"

        # 推进到待财务审批
        pending_finance = approval_scenarios.create_pending_at_finance(
            user_id=1, amount=1000.00, reason="状态流转测试"
        )
        assert pending_finance["status"] == "pending_at_finance"
        assert pending_finance["reimbursement"]["status"] == "dept_approved"

        # 推进到待总经理审批
        pending_ceo = approval_scenarios.create_pending_at_ceo(
            user_id=1, amount=1000.00, reason="状态流转测试"
        )
        assert pending_ceo["status"] == "pending_at_ceo"
        assert pending_ceo["reimbursement"]["status"] == "finance_approved"

    @allure.title("待部门审批场景 - 使用Fixture")
    def test_pending_at_dept_scenario(self, pending_at_dept):
        """测试待部门审批场景"""
        assert pending_at_dept["status"] == "pending_at_dept"
        assert pending_at_dept["reimbursement"]["status"] == "pending"

    @allure.title("待财务审批场景 - 使用Fixture")
    def test_pending_at_finance_scenario(self, pending_at_finance):
        """测试待财务审批场景"""
        assert pending_at_finance["status"] == "pending_at_finance"
        assert pending_at_finance["reimbursement"]["status"] == "dept_approved"

    @allure.title("待总经理审批场景 - 使用Fixture")
    def test_pending_at_ceo_scenario(self, pending_at_ceo):
        """测试待总经理审批场景"""
        assert pending_at_ceo["status"] == "pending_at_ceo"
        assert pending_at_ceo["reimbursement"]["status"] == "finance_approved"


@allure.feature("审批流")
@allure.story("审批依赖关系")
class TestApprovalDependencies(IntegrationTest):
    """审批依赖关系测试"""

    @allure.title("审批流程依赖关系验证")
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

    @allure.title("获取完整审批流程信息")
    def test_get_full_workflow(
        self, authenticated_client, fully_approved_reimbursement, ceo_approval_builder
    ):
        """测试获取完整审批流程信息"""
        reimbursement_id = fully_approved_reimbursement["reimbursement"]["id"]

        workflow = ceo_approval_builder.get_workflow(reimbursement_id)

        assert workflow is not None
        assert workflow["reimbursement"]["id"] == reimbursement_id
        assert workflow["dept_approval"]["reimbursement_id"] == reimbursement_id
        assert workflow["finance_approval"]["reimbursement_id"] == reimbursement_id
        assert workflow["ceo_approval"]["reimbursement_id"] == reimbursement_id


@allure.feature("审批流")
@allure.story("审批场景Fixtures")
class TestApprovalScenarioFixtures(IntegrationTest):
    """审批场景Fixtures测试"""

    @allure.title("完整审批通过场景")
    def test_full_approval_workflow_scenario(self, full_approval_workflow):
        """测试完整审批通过场景"""
        assert full_approval_workflow["status"] == "fully_approved"
        assert full_approval_workflow["reimbursement"]["status"] == "ceo_approved"

    @allure.title("部门拒绝场景")
    def test_dept_rejected_scenario(self, dept_rejected_workflow):
        """测试部门拒绝场景"""
        assert dept_rejected_workflow["status"] == "dept_rejected"
        assert dept_rejected_workflow["dept_approval"]["status"] == "rejected"

    @allure.title("财务拒绝场景")
    def test_finance_rejected_scenario(self, finance_rejected_workflow):
        """测试财务拒绝场景"""
        assert finance_rejected_workflow["status"] == "finance_rejected"
        assert finance_rejected_workflow["finance_approval"]["status"] == "rejected"

    @allure.title("总经理拒绝场景")
    def test_ceo_rejected_scenario(self, ceo_rejected_workflow):
        """测试总经理拒绝场景"""
        assert ceo_rejected_workflow["status"] == "ceo_rejected"
        assert ceo_rejected_workflow["ceo_approval"]["status"] == "rejected"

    @allure.title("多级审批流程集合")
    def test_multi_level_workflows(self, multi_level_workflows):
        """测试多级审批流程集合"""
        assert len(multi_level_workflows) == 4

        statuses = [w["status"] for w in multi_level_workflows.values()]
        assert "pending_at_dept" in statuses
        assert "pending_at_finance" in statuses
        assert "pending_at_ceo" in statuses
        assert "fully_approved" in statuses


@allure.feature("审批流")
@allure.story("审批依赖验证")
class TestApprovalDependencyValidation(IntegrationTest):
    """审批依赖验证测试"""

    @allure.title("不能跳过部门审批直接进行财务审批")
    def test_cannot_skip_dept_approval(
        self, authenticated_client, pending_reimbursement, finance_manager_id, ceo_id
    ):
        """测试不能跳过部门审批直接进行财务审批"""
        # 尝试直接进行财务审批（没有部门审批）
        demo_project.finance_approval.set_token(authenticated_client.token)
        result = demo_project.finance_approval.create_finance_approval(
            reimbursement_id=pending_reimbursement["id"],
            dept_approval_id=99999,  # 不存在的部门审批
            approver_id=finance_manager_id,
            status="approved",
            comment="测试",
        )
        assert result["code"] == 404

    @allure.title("不能跳过财务审批直接进行总经理审批")
    def test_cannot_skip_finance_approval(
        self, authenticated_client, dept_approved_reimbursement, ceo_id
    ):
        """测试不能跳过财务审批直接进行总经理审批"""
        # 尝试直接进行总经理审批（没有财务审批）
        demo_project.ceo_approval.set_token(authenticated_client.token)
        result = demo_project.ceo_approval.create_ceo_approval(
            reimbursement_id=dept_approved_reimbursement["reimbursement"]["id"],
            finance_approval_id=99999,  # 不存在的财务审批
            approver_id=ceo_id,
            status="approved",
            comment="测试",
        )
        assert result["code"] == 404

    @allure.title("部门拒绝后不能进行财务审批")
    def test_dept_rejected_cannot_proceed(
        self, authenticated_client, dept_rejected_reimbursement, finance_manager_id
    ):
        """测试部门拒绝后不能进行财务审批"""
        dept_approval_id = dept_rejected_reimbursement["dept_approval"]["id"]

        demo_project.finance_approval.set_token(authenticated_client.token)
        result = demo_project.finance_approval.create_finance_approval(
            reimbursement_id=dept_rejected_reimbursement["reimbursement"]["id"],
            dept_approval_id=dept_approval_id,
            approver_id=finance_manager_id,
            status="approved",
            comment="测试",
        )
        assert result["code"] == 400

    @allure.title("财务拒绝后不能进行总经理审批")
    def test_finance_rejected_cannot_proceed(
        self, authenticated_client, finance_rejected_reimbursement, ceo_id
    ):
        """测试财务拒绝后不能进行总经理审批"""
        finance_approval_id = finance_rejected_reimbursement["finance_approval"]["id"]

        demo_project.ceo_approval.set_token(authenticated_client.token)
        result = demo_project.ceo_approval.create_ceo_approval(
            reimbursement_id=finance_rejected_reimbursement["reimbursement"]["id"],
            finance_approval_id=finance_approval_id,
            approver_id=ceo_id,
            status="approved",
            comment="测试",
        )
        assert result["code"] == 400


@allure.feature("审批流")
@allure.story("审批流程参数化测试")
class TestApprovalParameterized(E2ETest):
    """审批流程参数化测试"""

    @allure.title("不同金额的审批流程")
    @pytest.mark.parametrize(
        "amount,expected_success",
        [
            pytest.param(100.00, True, id="small_amount"),
            pytest.param(1000.00, True, id="medium_amount"),
            pytest.param(10000.00, True, id="large_amount"),
        ],
    )
    def test_approval_with_different_amounts(
        self, approval_scenarios, test_context, amount, expected_success
    ):
        """参数化测试不同金额的审批流程"""
        workflow = approval_scenarios.create_full_approval_workflow(
            user_id=1,
            amount=amount,
            reason=f"金额测试 {amount}",
            approved=expected_success,
        )

        if expected_success:
            assert workflow["status"] == "fully_approved"

        test_context.set(f"workflow_{amount}", workflow)

    @allure.title("审批流程场景矩阵")
    def test_approval_scenario_matrix(
        self,
        full_approval_workflow,
        dept_rejected_workflow,
        finance_rejected_workflow,
        ceo_rejected_workflow,
    ):
        """测试审批流程场景矩阵"""
        # 验证所有场景fixture都正常工作
        assert full_approval_workflow["status"] == "fully_approved"
        assert dept_rejected_workflow["status"] == "dept_rejected"
        assert finance_rejected_workflow["status"] == "finance_rejected"
        assert ceo_rejected_workflow["status"] == "ceo_rejected"


@allure.feature("审批流")
@allure.story("审批流程性能测试")
class TestApprovalPerformance(E2ETest):
    """审批流程性能测试"""

    @allure.title("完整审批流程执行时间")
    def test_full_approval_performance(self, approval_scenarios):
        """测试完整审批流程执行时间"""
        import time

        start_time = time.time()

        workflow = approval_scenarios.create_full_approval_workflow(
            user_id=1, amount=5000.00, reason="性能测试"
        )

        end_time = time.time()
        duration = end_time - start_time

        assert workflow["status"] == "fully_approved"
        # 验证执行时间在合理范围内（开发环境放宽到30秒）
        assert duration < 30.0, f"审批流程执行时间过长: {duration}秒"

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

【新增】README 最新架构流程演示：
- Context 对象模式 - ctx.create(), ctx.use(), ctx.expect(), ctx.event()
- Scenario 依赖声明 - requires: Dependencies = [...]
- Scenario 业务编排 - orchestrate(self, ctx: Context)
- 变体矩阵 - VariantMatrix 参数化测试
"""

import allure
import pytest

from auto_tests.bdd_api_mock.api_manager import bdd_api_mock
from auto_tests.bdd_api_mock.data_factory.context import Context
from auto_tests.bdd_api_mock.data_factory.entities import UserEntity, ReimbursementEntity, OrgEntity, BudgetEntity
from auto_tests.bdd_api_mock.data_factory.scenarios import FullApprovalScenario, RejectionWorkflowScenario
from core.base.layering_base import IntegrationTest, E2ETest
from core.models import VariantMatrix, Dimension




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
        bdd_api_mock.finance_approval.set_token(authenticated_client.token)
        result = bdd_api_mock.finance_approval.create_finance_approval(
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
        bdd_api_mock.ceo_approval.set_token(authenticated_client.token)
        result = bdd_api_mock.ceo_approval.create_ceo_approval(
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

        bdd_api_mock.finance_approval.set_token(authenticated_client.token)
        result = bdd_api_mock.finance_approval.create_finance_approval(
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

        bdd_api_mock.ceo_approval.set_token(authenticated_client.token)
        result = bdd_api_mock.ceo_approval.create_ceo_approval(
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


# =============================================================================
# 【新增】README 最新架构流程演示
# =============================================================================


@allure.feature("审批流-新架构")
@allure.story("Context对象模式")
class TestApprovalWithContext(E2ETest):
    """
    使用 Context 对象模式执行审批流程

    展示 README 中描述的：
    - ctx.create() - 创建实体
    - ctx.use() - 复用实体
    - ctx.expect() - 验证预期
    - ctx.event() - 事件追踪
    """

    @allure.title("完整审批流程 - Context对象")
    def test_full_approval_with_context(self, authenticated_client, test_context):
        """使用 Context 对象执行完整审批流程"""
        ctx = Context(auto_cleanup=True, enable_lineage=True)

        with ctx:
            # 1. 创建依赖实体
            submitter = ctx.create(
                UserEntity,
                username="employee_ctx",
                role="employee",
                email="employee@ctx.com",
                full_name="Context Employee",
                password="123456",
            )

            approver_dept = ctx.create(
                UserEntity,
                username="manager_ctx",
                role="manager",
                email="manager@ctx.com",
                full_name="Context Manager",
                password="123456",
            )

            org = ctx.create(
                OrgEntity,
                name="Context Org",
                code="CTX001",
                budget_total=1000000,
                level=1,
            )

            budget = ctx.create(
                BudgetEntity,
                org_id=org.id,
                total_amount=500000,
                category="project",
                year=2026,
                status="active",
            )

            # 2. 创建报销申请
            reimb = ctx.create(
                ReimbursementEntity,
                user_id=submitter.id,
                amount=5000.00,
                reason="Context模式测试",
                status="pending",
            )

            # 3. 验证预算充足
            has_budget = ctx.expect(budget.get_available_amount()).gt(5000.00)
            assert has_budget, "预算不足"

            # 4. 模拟审批流程
            reimb.status = "pending"
            ctx.fire_event("submitted", priority="normal")

            reimb.status = "dept_approved"
            ctx.fire_event("dept_approved", priority="normal")

            reimb.status = "finance_approved"
            ctx.fire_event("finance_approved", priority="normal")

            reimb.status = "ceo_approved"
            ctx.fire_event("ceo_approved", priority="high")

            # 5. 消耗预算
            budget.consume(5000.00)

            # 6. 验证最终结果
            assert ctx.expect(reimb.status).equals("ceo_approved")
            assert ctx.event("ceo_approved").was_fired()

            test_context.set(
                "context_workflow",
                {
                    "status": reimb.status,
                    "reimbursement_id": reimb.id,
                    "budget_remaining": budget.get_available_amount(),
                },
            )


@allure.feature("审批流-新架构")
@allure.story("Scenario依赖声明与编排")
class TestApprovalWithScenario(E2ETest):
    """
    使用 Scenario 的依赖声明和业务编排

    展示 README 中描述的：
    - requires: Dependencies - 依赖声明
    - orchestrate() - 业务编排
    - 自动依赖解决
    """

    @allure.title("完整审批流程 - FullApprovalScenario")
    def test_full_approval_scenario(self, authenticated_client, test_context):
        """使用 FullApprovalScenario 执行完整审批流程"""
        scenario = FullApprovalScenario(
            token=authenticated_client.token,
            amount=5000.00,
            priority="normal",
            requires_ceo=True,
        )

        # 执行场景（自动解决依赖并调用 orchestrate）
        result = scenario.execute()

        # 验证结果
        assert result.success, f"场景执行失败: {result.errors}"

        # 验证创建的实体
        reimb = result.get_entity("reimbursement")
        assert reimb is not None
        assert reimb.status == "ceo_approved"

        # 验证审批人
        assert result.get_entity("approver_dept") is not None
        assert result.get_entity("approver_finance") is not None
        assert result.get_entity("approver_ceo") is not None

        test_context.set("scenario_result", result)

    @allure.title("预算不足场景")
    def test_budget_insufficient(self, authenticated_client, test_context):
        """测试预算不足场景"""
        scenario = FullApprovalScenario(
            token=authenticated_client.token,
            amount=1000000,  # 超过预算
            priority="normal",
        )

        result = scenario.execute()

        # 预算检查应该失败
        assert not result.success or result.data.get("budget_check") == "failed"

        test_context.set("budget_result", result)

    @allure.title("拒绝流程 - RejectionWorkflowScenario")
    def test_rejection_scenario(self, authenticated_client, test_context):
        """使用 RejectionWorkflowScenario 测试拒绝流程"""
        scenario = RejectionWorkflowScenario(token=authenticated_client.token)

        result = scenario.execute(
            reject_at="dept", user_id=1, amount=1000.00, reason="拒绝流程测试"
        )

        assert result.success
        assert result.data.get("rejected_at") == "dept"
        assert result.data.get("final_status") == "dept_rejected"

        test_context.set("rejection_result", result)


@allure.feature("审批流-新架构")
@allure.story("变体矩阵参数化测试")
class TestApprovalWithVariantMatrix(E2ETest):
    """
    使用变体矩阵进行参数化测试

    展示 README 中描述的 VariantMatrix：
    - Dimension - 维度定义
    - Variant - 变体定义
    - 笛卡尔积生成所有组合
    """

    @allure.title("变体矩阵 - 手动遍历")
    def test_variant_matrix_manual(self, authenticated_client, test_context):
        """手动遍历变体矩阵的所有组合"""
        # 获取所有变体
        variants = FullApprovalScenario.all_variants()

        results = []
        for variant in variants:
            variant_name = variant.get("name", "unknown")
            params = variant.get("params", {})

            # 创建场景并执行
            scenario = FullApprovalScenario(
                token=authenticated_client.token,
                amount=params.get("amount", 1000),
                priority=params.get("priority", "normal"),
                requires_ceo=params.get("requires_ceo", False),
            )

            result = scenario.execute()
            results.append((variant_name, result))

            assert result.success, f"变体 {variant_name} 执行失败"

        test_context.set("variant_results", results)
        assert len(results) == 6, f"预期 6 个变体，实际 {len(results)}"

    @allure.title("变体矩阵 - 指定变体")
    def test_specific_variant(self, authenticated_client, test_context):
        """测试指定变体 - 使用 small + urgent 组合（避免预算不足）"""
        # 获取所有变体
        all_variants = FullApprovalScenario.all_variants()

        # 找到 small + urgent 变体（避免预算不足问题）
        target_values = None
        for variant in all_variants:
            # variant 是字典，包含 'amount' 和 'urgency' 两个 Variant 对象
            amount_variant = variant.get("amount")
            urgency_variant = variant.get("urgency")

            # 检查是否是 small + urgent 组合
            if (
                    amount_variant
                    and amount_variant.get("amount") == 1000
                    and urgency_variant
                    and urgency_variant.get("priority") == "high"
            ):
                # 合并两个变体的 values
                target_values = {**amount_variant.values, **urgency_variant.values}
                break

        # 如果没找到，使用第一个 small 变体
        if target_values is None:
            for variant in all_variants:
                amount_variant = variant.get("amount")
                if amount_variant and amount_variant.get("amount") == 1000:
                    urgency_variant = variant.get("urgency")
                    target_values = {**amount_variant.values, **urgency_variant.values}
                    break

        assert target_values is not None, "未找到 small 变体"

        # 验证变体属性
        assert target_values.get("requires_ceo") is False, "small 金额不需要 CEO 审批"
        assert target_values.get("amount") == 1000

        # 执行场景
        scenario = FullApprovalScenario(
            token=authenticated_client.token,
            amount=target_values.get("amount", 1000),
            priority="urgent",  # high 对应 urgent
            requires_ceo=False,
        )

        result = scenario.execute()
        assert result.success, f"场景执行失败: {result.message}"
        assert (
                result.data.get("final_status") == "finance_approved"
        )  # small 金额不需要 CEO 审批

        test_context.set("specific_variant", result)

    @allure.title("自定义变体矩阵")
    def test_custom_variant_matrix(self, authenticated_client, test_context):
        """创建自定义变体矩阵"""
        # 创建自定义变体矩阵
        matrix = VariantMatrix(
            [
                Dimension("amount_level", ["low", "high"]),
                Dimension("approval_type", ["normal", "fast"]),
            ]
        )

        # 生成所有组合
        variants = matrix.generate()
        assert len(variants) == 4  # 2 × 2

        # 定义参数映射
        param_map = {
            ("low", "normal"): {
                "amount": 100,
                "requires_ceo": False,
                "priority": "normal",
            },
            ("low", "fast"): {
                "amount": 100,
                "requires_ceo": False,
                "priority": "urgent",
            },
            ("high", "normal"): {
                "amount": 50000,
                "requires_ceo": True,
                "priority": "normal",
            },
            ("high", "fast"): {
                "amount": 50000,
                "requires_ceo": True,
                "priority": "urgent",
            },
        }

        results = []
        for variant in variants:
            key = (variant.get("amount_level"), variant.get("approval_type"))
            params = param_map.get(
                key, {"amount": 1000, "requires_ceo": False, "priority": "normal"}
            )

            scenario = FullApprovalScenario(
                token=authenticated_client.token,
                amount=params.get("amount", 1000),
                priority=params.get("priority", "normal"),
                requires_ceo=params.get("requires_ceo", False),
            )

            result = scenario.execute()
            results.append(result)
            assert result.success

        test_context.set("custom_matrix_results", results)


@allure.feature("审批流-新架构")
@allure.story("依赖自动解决")
class TestDependencyResolution(E2ETest):
    """
    测试依赖自动解决机制

    FullApprovalScenario.requires = [UserEntity, OrgEntity, BudgetEntity]
    """

    @allure.title("自动解决依赖")
    def test_auto_resolve_deps(self, authenticated_client, test_context):
        """测试自动依赖解决"""
        scenario = FullApprovalScenario(token=authenticated_client.token)

        # 执行前检查依赖
        submitter_before = scenario.get_dependency("submitter")

        # 执行场景（自动解决依赖）
        result = scenario.execute(amount=1000.00)

        # 验证依赖已解决
        assert result.success
        assert scenario.get_dependency("submitter") is not None
        assert scenario.get_dependency("org") is not None
        assert scenario.get_dependency("budget") is not None

        test_context.set("dep_result", result)

    @allure.title("手动注入依赖")
    def test_manual_dependency(self, authenticated_client, test_context):
        """测试手动依赖注入"""
        # 创建自定义依赖
        custom_user = UserEntity(
            username="custom_user",
            role="employee",
            email="custom@test.com",
            full_name="Custom User",
            password="123456",
        )

        scenario = FullApprovalScenario(token=authenticated_client.token)

        # 手动注入依赖
        scenario._resolved_deps["submitter"] = custom_user

        # 执行
        result = scenario.execute(amount=1000.00)

        # 验证使用了手动注入的依赖
        submitter = scenario.get_dependency("submitter")
        assert submitter.username == "custom_user"

        test_context.set("manual_dep_result", result)

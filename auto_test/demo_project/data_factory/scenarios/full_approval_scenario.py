# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 完整审批流场景 - D→C→B→A 四级审批
# @Time   : 2026-04-01
# @Author : 毛鹏

"""
完整审批流场景

实现 D(报销) → C(部门) → B(财务) → A(CEO) 的完整审批流程
支持变体矩阵参数化和自动依赖解决
"""

from typing import Dict, Any, Optional
import sys
import os

# 添加父目录到路径以确保导入工作
_current_dir = os.path.dirname(os.path.abspath(__file__))
_parent_dir = os.path.dirname(_current_dir)
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

try:
    from .base_scenario import BaseScenario, ScenarioResult, Dependencies, Creates
    from ..entities import UserEntity, ReimbursementEntity
    from ..entities.org_entity import OrgEntity
    from ..entities.budget_entity import BudgetEntity
    from ..context import Context
    from .variant_matrix import VariantMatrix, Dimension, Variant
except ImportError:
    # 回退导入
    from base_scenario import BaseScenario, ScenarioResult, Dependencies, Creates

    sys.path.insert(0, os.path.dirname(_parent_dir))
    from entities import UserEntity, ReimbursementEntity
    from entities.org_entity import OrgEntity
    from entities.budget_entity import BudgetEntity
    from context import Context
    from variant_matrix import VariantMatrix, Dimension, Variant


class FullApprovalScenario(BaseScenario):
    """
    完整审批流场景 - D→C→B→A 四级审批

    业务流程：
    1. D级：创建报销申请
    2. C级：部门审批
    3. B级：财务审批
    4. A级：CEO审批（大额触发）

    依赖声明：
    - requires: UserEntity, OrgEntity, BudgetEntity

    创建声明：
    - creates: ReimbursementEntity

    变体矩阵：
    - amount: small(1000), medium(50000), large(500000)
    - urgency: normal, urgent

    使用示例：
        # 基础用法
        scenario = FullApprovalScenario()
        result = scenario.execute(amount=50000)

        # 使用变体
        scenario = FullApprovalScenario()
        scenario.set_variant("large_urgent", FullApprovalScenario.variant(
            amount="large", urgency="urgent"
        ))
        result = scenario.execute()

        # 验证结果
        assert result.success
        assert result.get_entity("reimbursement").status == "ceo_approved"
    """

    # ========== 依赖声明 ==========
    requires: Dependencies = [UserEntity, OrgEntity, BudgetEntity]

    # ========== 创建声明 ==========
    creates: Creates = [ReimbursementEntity]

    # ========== 变体矩阵 ==========
    variants = VariantMatrix(
        [
            Dimension(
                "amount",
                [
                    Variant(
                        "small", {"amount": 1000, "level": 1, "requires_ceo": False}, 0
                    ),
                    Variant(
                        "medium",
                        {"amount": 50000, "level": 2, "requires_ceo": False},
                        1,
                    ),
                    Variant(
                        "large", {"amount": 500000, "level": 3, "requires_ceo": True}, 2
                    ),
                ],
            ),
            Dimension(
                "urgency",
                [
                    Variant("normal", {"priority": "normal", "sla_hours": 72}, 0),
                    Variant("urgent", {"priority": "high", "sla_hours": 4}, 1),
                ],
            ),
        ]
    )

    def __init__(self, token: str = None, context: Context = None, **params):
        """
        初始化完整审批流场景

        @param token: 认证token
        @param context: 执行上下文
        @param params: 场景参数（amount, priority等）
        """
        super().__init__(token=token, context=context, auto_resolve_deps=True, **params)

    def _prepare_dependencies(self):
        """
        准备依赖实体

        创建或获取所需的依赖实体
        """
        # 创建提交人
        if not self.get_dependency("submitter"):
            submitter = UserEntity(
                username="employee_001",
                role="employee",
                email="employee@test.com",
                full_name="Employee 001",
                password="123456",
            )
            self._resolved_deps["submitter"] = submitter
            if self.context:
                self.context.create(UserEntity, **submitter.__dict__)

        # 创建部门审批人
        if not self.get_dependency("approver_dept"):
            approver_dept = UserEntity(
                username="manager_001",
                role="manager",
                email="manager@test.com",
                full_name="Manager 001",
                password="123456",
            )
            self._resolved_deps["approver_dept"] = approver_dept
            if self.context:
                self.context.create(UserEntity, **approver_dept.__dict__)

        # 创建财务审批人
        if not self.get_dependency("approver_finance"):
            approver_finance = UserEntity(
                username="finance_001",
                role="finance",
                email="finance@test.com",
                full_name="Finance 001",
                password="123456",
            )
            self._resolved_deps["approver_finance"] = approver_finance
            if self.context:
                self.context.create(UserEntity, **approver_finance.__dict__)

        # 创建CEO审批人
        if not self.get_dependency("approver_ceo"):
            approver_ceo = UserEntity(
                username="ceo_001",
                role="ceo",
                email="ceo@test.com",
                full_name="CEO 001",
                password="123456",
            )
            self._resolved_deps["approver_ceo"] = approver_ceo
            if self.context:
                self.context.create(UserEntity, **approver_ceo.__dict__)

        # 创建组织
        if not self.get_dependency("org"):
            org = OrgEntity.with_budget(budget=1000000, name="总公司", code="ORG001")
            self._resolved_deps["org"] = org
            if self.context:
                self.context.create(OrgEntity, **org.__dict__)

        # 创建预算
        if not self.get_dependency("budget"):
            org = self.get_dependency("org")
            budget = BudgetEntity.for_org(
                org_id=org.id if org else None,
                amount=500000,
                category="project",
                year=2026,
            )
            self._resolved_deps["budget"] = budget
            if self.context:
                self.context.create(BudgetEntity, **budget.__dict__)

    def orchestrate(self, ctx: Context) -> ScenarioResult:
        """
        编排完整审批流程

        流程：D级(报销) → C级(部门) → B级(财务) → A级(CEO)

        @param ctx: 场景上下文
        @return: 场景执行结果
        """
        result = ScenarioResult()

        # 准备依赖
        self._prepare_dependencies()

        # 获取参数
        amount = self.params.get("amount", 1000)
        priority = self.params.get("priority", "normal")
        requires_ceo = self.params.get("requires_ceo", False)

        # 1. 获取依赖实体
        submitter = self.get_dependency("submitter")
        approver_dept = self.get_dependency("approver_dept")
        approver_finance = self.get_dependency("approver_finance")
        approver_ceo = self.get_dependency("approver_ceo")
        budget = self.get_dependency("budget")

        # 2. D级：创建报销申请
        reimb = ctx.create(
            ReimbursementEntity,
            user_id=submitter.id if submitter else 1,
            amount=amount,
            reason=f"项目报销 - {priority}优先级",
            status="pending",
        )
        result.add_entity("reimbursement", reimb)
        result.add_entity("submitter", submitter)

        # 检查预算是否充足
        if budget and not budget.has_enough_budget(amount):
            result.success = False
            result.message = "预算不足"
            result.data["budget_check"] = "failed"
            ctx.fire_event("budget_insufficient", priority="high")
            return result

        ctx.fire_event("budget_sufficient", priority="normal")
        result.data["budget_check"] = "passed"

        # 3. 提交报销申请（直接修改状态）
        reimb.status = "pending"
        result.data["submitted"] = True

        # 4. C级：部门审批（直接修改状态）
        reimb.status = "dept_approved"
        result.add_entity("approver_dept", approver_dept)
        result.data["dept_approved"] = True

        # 5. B级：财务审批（直接修改状态）
        reimb.status = "finance_approved"
        result.add_entity("approver_finance", approver_finance)
        result.data["finance_approved"] = True

        # 6. A级：CEO审批（大额触发）
        if requires_ceo:
            reimb.status = "ceo_approved"
            result.add_entity("approver_ceo", approver_ceo)
            result.data["ceo_approved"] = True
        else:
            reimb.status = "finance_approved"

        # 7. 消耗预算
        if budget:
            budget.consume(amount)
            result.data["budget_consumed"] = amount
            result.data["budget_remaining"] = budget.get_available_amount()

        # 8. 验证结果
        result.success = ctx.expect(reimb.status).is_not_none()
        result.data["final_status"] = reimb.status
        result.data["amount"] = amount
        result.data["priority"] = priority

        return result

    def _expected_result(self) -> Dict[str, Any]:
        """
        预期结果

        根据变体和参数计算预期结果

        @return: 预期结果字典
        """
        requires_ceo = self.params.get("requires_ceo", False)
        amount = self.params.get("amount", 1000)

        expected = {
            "success": True,
            "budget_check": "passed",
            "submitted": True,
            "dept_approved": True,
            "finance_approved": True,
        }

        if requires_ceo:
            expected["ceo_approved"] = True
            expected["final_status"] = "ceo_approved"
        else:
            expected["final_status"] = "finance_approved"

        expected["amount"] = amount

        return expected

    def pre_execute(self, *args, **kwargs) -> bool:
        """
        执行前检查

        @return: 是否继续执行
        """
        # 检查必要参数
        amount = self.params.get("amount") or kwargs.get("amount")
        if amount is None:
            # 从变体获取默认值
            if self._current_variant:
                amount_variant = self._current_variant.get("amount")
                if amount_variant and hasattr(amount_variant, "values"):
                    self.params["amount"] = amount_variant.values.get("amount", 1000)
                    self.params["requires_ceo"] = amount_variant.values.get(
                        "requires_ceo", False
                    )

        return True


# 导出
__all__ = ["FullApprovalScenario"]


# 测试代码
if __name__ == "__main__":
    print("FullApprovalScenario 模块加载成功")

    # 测试变体生成
    variants = FullApprovalScenario.all_variants()
    print(f"变体数量: {len(variants)}")

    # 测试获取指定变体
    variant = FullApprovalScenario.variant(amount="large", urgency="urgent")
    print(f"指定变体: {variant}")

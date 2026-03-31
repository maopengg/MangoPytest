# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 审批流场景 - 4级审批依赖场景
# @Time   : 2026-03-31
# @Author : 毛鹏
from typing import Dict, Any, Optional, List

from .base_scenario import BaseScenario
from ..builders.reimbursement import ReimbursementBuilder
from ..builders.dept_approval import DeptApprovalBuilder
from ..builders.finance_approval import FinanceApprovalBuilder
from ..builders.ceo_approval import CEOApprovalBuilder


class ApprovalScenarios(BaseScenario):
    """
    审批流场景类
    提供4级审批依赖的完整场景：
    D级：Reimbursement（报销申请）
    C级：DeptApproval（部门审批）依赖D级
    B级：FinanceApproval（财务审批）依赖C级
    A级：CEOApproval（总经理审批）依赖B级
    """

    def __init__(self, token: str = None, factory=None):
        super().__init__(token, factory)
        # 初始化各级builder
        self.reimbursement_builder = ReimbursementBuilder(token, factory)
        self.dept_approval_builder = DeptApprovalBuilder(token, factory)
        self.finance_approval_builder = FinanceApprovalBuilder(token, factory)
        self.ceo_approval_builder = CEOApprovalBuilder(token, factory)

    def create_full_approval_workflow(self, user_id: int = 1, amount: float = 1000.00,
                                      reason: str = None, approved: bool = True) -> Dict[str, Any]:
        """
        创建完整的4级审批流程
        D -> C -> B -> A

        @param user_id: 申请人ID
        @param amount: 报销金额
        @param reason: 报销原因
        @param approved: 是否全部通过（False则在某级拒绝）
        @return: 完整的审批流程数据
        """
        # D级：创建报销申请
        reimbursement = self.reimbursement_builder.create(user_id, amount, reason)
        if not reimbursement:
            return {"error": "创建报销申请失败"}

        reimbursement_id = reimbursement["id"]

        # C级：部门审批
        dept_approval = self.dept_approval_builder.approve(reimbursement_id)
        if not dept_approval:
            return {"error": "部门审批失败", "reimbursement": reimbursement}

        if not approved:
            # 模拟在部门审批后拒绝
            return {
                "reimbursement": reimbursement,
                "dept_approval": dept_approval,
                "status": "dept_rejected_simulated"
            }

        dept_approval_id = dept_approval["id"]

        # B级：财务审批
        finance_approval = self.finance_approval_builder.approve(reimbursement_id, dept_approval_id)
        if not finance_approval:
            return {"error": "财务审批失败", "reimbursement": reimbursement, "dept_approval": dept_approval}

        finance_approval_id = finance_approval["id"]

        # A级：总经理审批
        ceo_approval = self.ceo_approval_builder.approve(reimbursement_id, finance_approval_id)
        if not ceo_approval:
            return {"error": "总经理审批失败", "reimbursement": reimbursement,
                    "dept_approval": dept_approval, "finance_approval": finance_approval}

        return {
            "reimbursement": reimbursement,
            "dept_approval": dept_approval,
            "finance_approval": finance_approval,
            "ceo_approval": ceo_approval,
            "status": "fully_approved"
        }

    def create_dept_rejected_workflow(self, user_id: int = 1, amount: float = 1000.00,
                                      reason: str = None, comment: str = "部门审核不通过") -> Dict[str, Any]:
        """
        创建部门审批拒绝的场景
        D -> C(rejected)

        @param user_id: 申请人ID
        @param amount: 报销金额
        @param reason: 报销原因
        @param comment: 拒绝原因
        @return: 审批流程数据
        """
        # D级：创建报销申请
        reimbursement = self.reimbursement_builder.create(user_id, amount, reason)
        if not reimbursement:
            return {"error": "创建报销申请失败"}

        # C级：部门审批拒绝
        dept_approval = self.dept_approval_builder.reject(reimbursement["id"], comment=comment)
        if not dept_approval:
            return {"error": "部门审批拒绝失败", "reimbursement": reimbursement}

        return {
            "reimbursement": reimbursement,
            "dept_approval": dept_approval,
            "status": "dept_rejected"
        }

    def create_finance_rejected_workflow(self, user_id: int = 1, amount: float = 1000.00,
                                         reason: str = None, comment: str = "财务审核不通过") -> Dict[str, Any]:
        """
        创建财务审批拒绝的场景
        D -> C -> B(rejected)

        @param user_id: 申请人ID
        @param amount: 报销金额
        @param reason: 报销原因
        @param comment: 拒绝原因
        @return: 审批流程数据
        """
        # D级：创建报销申请
        reimbursement = self.reimbursement_builder.create(user_id, amount, reason)
        if not reimbursement:
            return {"error": "创建报销申请失败"}

        # C级：部门审批通过
        dept_approval = self.dept_approval_builder.approve(reimbursement["id"])
        if not dept_approval:
            return {"error": "部门审批失败", "reimbursement": reimbursement}

        # B级：财务审批拒绝
        finance_approval = self.finance_approval_builder.reject(
            reimbursement["id"], dept_approval["id"], comment=comment
        )
        if not finance_approval:
            return {"error": "财务审批拒绝失败", "reimbursement": reimbursement,
                    "dept_approval": dept_approval}

        return {
            "reimbursement": reimbursement,
            "dept_approval": dept_approval,
            "finance_approval": finance_approval,
            "status": "finance_rejected"
        }

    def create_ceo_rejected_workflow(self, user_id: int = 1, amount: float = 1000.00,
                                     reason: str = None, comment: str = "金额过大，不予批准") -> Dict[str, Any]:
        """
        创建总经理审批拒绝的场景
        D -> C -> B -> A(rejected)

        @param user_id: 申请人ID
        @param amount: 报销金额
        @param reason: 报销原因
        @param comment: 拒绝原因
        @return: 审批流程数据
        """
        # D级：创建报销申请
        reimbursement = self.reimbursement_builder.create(user_id, amount, reason)
        if not reimbursement:
            return {"error": "创建报销申请失败"}

        # C级：部门审批通过
        dept_approval = self.dept_approval_builder.approve(reimbursement["id"])
        if not dept_approval:
            return {"error": "部门审批失败", "reimbursement": reimbursement}

        # B级：财务审批通过
        finance_approval = self.finance_approval_builder.approve(
            reimbursement["id"], dept_approval["id"]
        )
        if not finance_approval:
            return {"error": "财务审批失败", "reimbursement": reimbursement,
                    "dept_approval": dept_approval}

        # A级：总经理审批拒绝
        ceo_approval = self.ceo_approval_builder.reject(
            reimbursement["id"], finance_approval["id"], comment=comment
        )
        if not ceo_approval:
            return {"error": "总经理审批拒绝失败", "reimbursement": reimbursement,
                    "dept_approval": dept_approval, "finance_approval": finance_approval}

        return {
            "reimbursement": reimbursement,
            "dept_approval": dept_approval,
            "finance_approval": finance_approval,
            "ceo_approval": ceo_approval,
            "status": "ceo_rejected"
        }

    def create_pending_at_dept(self, user_id: int = 1, amount: float = 1000.00,
                               reason: str = None) -> Dict[str, Any]:
        """
        创建待部门审批的场景
        D(created) -> pending at C

        @param user_id: 申请人ID
        @param amount: 报销金额
        @param reason: 报销原因
        @return: 报销申请数据
        """
        reimbursement = self.reimbursement_builder.create(user_id, amount, reason)
        if not reimbursement:
            return {"error": "创建报销申请失败"}

        return {
            "reimbursement": reimbursement,
            "status": "pending_at_dept"
        }

    def create_pending_at_finance(self, user_id: int = 1, amount: float = 1000.00,
                                  reason: str = None) -> Dict[str, Any]:
        """
        创建待财务审批的场景
        D -> C(approved) -> pending at B

        @param user_id: 申请人ID
        @param amount: 报销金额
        @param reason: 报销原因
        @return: 审批流程数据
        """
        # D级：创建报销申请
        reimbursement = self.reimbursement_builder.create(user_id, amount, reason)
        if not reimbursement:
            return {"error": "创建报销申请失败"}

        # C级：部门审批通过
        dept_approval = self.dept_approval_builder.approve(reimbursement["id"])
        if not dept_approval:
            return {"error": "部门审批失败", "reimbursement": reimbursement}

        return {
            "reimbursement": reimbursement,
            "dept_approval": dept_approval,
            "status": "pending_at_finance"
        }

    def create_pending_at_ceo(self, user_id: int = 1, amount: float = 1000.00,
                              reason: str = None) -> Dict[str, Any]:
        """
        创建待总经理审批的场景
        D -> C -> B(approved) -> pending at A

        @param user_id: 申请人ID
        @param amount: 报销金额
        @param reason: 报销原因
        @return: 审批流程数据
        """
        # D级：创建报销申请
        reimbursement = self.reimbursement_builder.create(user_id, amount, reason)
        if not reimbursement:
            return {"error": "创建报销申请失败"}

        # C级：部门审批通过
        dept_approval = self.dept_approval_builder.approve(reimbursement["id"])
        if not dept_approval:
            return {"error": "部门审批失败", "reimbursement": reimbursement}

        # B级：财务审批通过
        finance_approval = self.finance_approval_builder.approve(
            reimbursement["id"], dept_approval["id"]
        )
        if not finance_approval:
            return {"error": "财务审批失败", "reimbursement": reimbursement,
                    "dept_approval": dept_approval}

        return {
            "reimbursement": reimbursement,
            "dept_approval": dept_approval,
            "finance_approval": finance_approval,
            "status": "pending_at_ceo"
        }

    def get_workflow_status(self, reimbursement_id: int) -> Dict[str, Any]:
        """
        获取审批流程的完整状态
        @param reimbursement_id: 报销申请ID
        @return: 完整流程状态
        """
        return self.ceo_approval_builder.get_workflow(reimbursement_id)

    def cleanup_workflow(self, reimbursement_id: int) -> bool:
        """
        清理审批流程相关的所有数据
        注意：由于依赖关系，实际删除可能受限制
        @param reimbursement_id: 报销申请ID
        @return: 是否清理成功
        """
        # 获取完整流程
        workflow = self.get_workflow_status(reimbursement_id)

        # 按依赖顺序清理（从高层到低层）
        # A级
        ceo_approval = workflow.get("ceo_approval")
        if ceo_approval:
            self.ceo_approval_builder._register_created(ceo_approval)

        # B级
        finance_approval = workflow.get("finance_approval")
        if finance_approval:
            self.finance_approval_builder._register_created(finance_approval)

        # C级
        dept_approval = workflow.get("dept_approval")
        if dept_approval:
            self.dept_approval_builder._register_created(dept_approval)

        # D级
        reimbursement = workflow.get("reimbursement")
        if reimbursement:
            self.reimbursement_builder._register_created(reimbursement)

        return True

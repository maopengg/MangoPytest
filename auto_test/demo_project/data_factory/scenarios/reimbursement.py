# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 报销审批场景 - 4级审批流程
# @Time   : 2026-03-31
# @Author : 毛鹏
from typing import Optional, List

from .base_scenario import BaseScenario, ScenarioResult
from ..entities.reimbursement import ReimbursementEntity
from ..entities.dept_approval import DeptApprovalEntity
from ..entities.finance_approval import FinanceApprovalEntity
from ..entities.ceo_approval import CEOApprovalEntity
from ...api_manager import demo_project


class CreateReimbursementScenario(BaseScenario):
    """
    创建报销申请场景 - D级

    封装创建报销申请的流程
    """

    def _set_token(self):
        """设置token到API模块"""
        if self.token:
            demo_project.reimbursement.set_token(self.token)
            demo_project.dept_approval.set_token(self.token)
            demo_project.finance_approval.set_token(self.token)
            demo_project.ceo_approval.set_token(self.token)

    def execute(self, user_id: int, amount: float, reason: str) -> ScenarioResult:
        """
        执行创建报销申请场景

        @param user_id: 申请人ID
        @param amount: 报销金额
        @param reason: 报销原因
        @return: 场景执行结果
        """
        result = ScenarioResult()

        # 设置token
        self._set_token()

        # 创建实体
        entity = ReimbursementEntity(user_id=user_id, amount=amount, reason=reason)

        if not entity.validate():
            result.add_error("报销申请数据验证失败")
            return result

        # 调用API - 直接使用参数
        response = demo_project.reimbursement.create_reimbursement(
            user_id=user_id, amount=amount, reason=reason
        )

        if response.get("code") == 200:
            data = response["data"]
            entity = ReimbursementEntity.from_api_response(data)
            self.register_entity(entity)
            result.add_entity("reimbursement", entity)
            result.data = {"reimbursement_id": entity.id}
            result.message = "报销申请创建成功"
        else:
            result.add_error(f"报销申请创建失败: {response.get('message')}")

        return result


class FullApprovalWorkflowScenario(BaseScenario):
    """
    完整审批流程场景 - D->C->B->A

    封装4级审批的完整流程
    """

    def _set_token(self):
        """设置token到API模块"""
        if self.token:
            demo_project.reimbursement.set_token(self.token)
            demo_project.dept_approval.set_token(self.token)
            demo_project.finance_approval.set_token(self.token)
            demo_project.ceo_approval.set_token(self.token)

    def execute(
        self,
        user_id: int = 1,
        amount: float = 1000.00,
        reason: str = None,
        approvers: dict = None,
    ) -> ScenarioResult:
        """
        执行完整审批流程

        @param user_id: 申请人ID
        @param amount: 报销金额
        @param reason: 报销原因
        @param approvers: 审批人配置 {dept_id, finance_id, ceo_id}
        @return: 场景执行结果
        """
        import uuid

        result = ScenarioResult()

        # 设置token
        self._set_token()

        reason = reason or f"报销申请 - {uuid.uuid4().hex[:6]}"
        approvers = approvers or {"dept_id": 3, "finance_id": 4, "ceo_id": 5}

        # D级：创建报销申请
        create_scenario = CreateReimbursementScenario(self.token, self.factory)
        create_result = create_scenario.execute(user_id, amount, reason)

        if not create_result.success:
            result.add_error(f"创建报销申请失败: {create_result.errors}")
            return result

        reimbursement = create_result.get_entity("reimbursement")
        result.add_entity("reimbursement", reimbursement)

        # C级：部门审批
        dept_response = demo_project.dept_approval.create_dept_approval(
            reimbursement_id=reimbursement.id,
            approver_id=approvers["dept_id"],
            status="approved",
            comment="部门审批通过",
        )

        if dept_response.get("code") == 200:
            dept_data = dept_response["data"]
            dept_entity = DeptApprovalEntity.from_api_response(dept_data)
            self.register_entity(dept_entity)
            result.add_entity("dept_approval", dept_entity)
        else:
            result.add_error(f"部门审批创建失败: {dept_response.get('message')}")
            return result

        # B级：财务审批
        finance_response = demo_project.finance_approval.create_finance_approval(
            reimbursement_id=reimbursement.id,
            dept_approval_id=dept_entity.id,
            approver_id=approvers["finance_id"],
            status="approved",
            comment="财务审批通过",
        )

        if finance_response.get("code") == 200:
            finance_data = finance_response["data"]
            finance_entity = FinanceApprovalEntity.from_api_response(finance_data)
            self.register_entity(finance_entity)
            result.add_entity("finance_approval", finance_entity)
        else:
            result.add_error(f"财务审批创建失败: {finance_response.get('message')}")
            return result

        # A级：总经理审批
        ceo_response = demo_project.ceo_approval.create_ceo_approval(
            reimbursement_id=reimbursement.id,
            finance_approval_id=finance_entity.id,
            approver_id=approvers["ceo_id"],
            status="approved",
            comment="总经理审批通过",
        )

        if ceo_response.get("code") == 200:
            ceo_data = ceo_response["data"]
            ceo_entity = CEOApprovalEntity.from_api_response(ceo_data)
            self.register_entity(ceo_entity)
            result.add_entity("ceo_approval", ceo_entity)
        else:
            result.add_error(f"总经理审批创建失败: {ceo_response.get('message')}")
            return result

        # 重新获取报销申请的最新状态
        reimbursement_response = demo_project.reimbursement.get_reimbursement_by_id(
            reimbursement.id
        )
        if reimbursement_response.get("code") == 200:
            updated_reimbursement = ReimbursementEntity.from_api_response(
                reimbursement_response["data"]
            )
            result.add_entity("reimbursement", updated_reimbursement)

        result.message = "完整审批流程执行成功"
        result.data = {
            "reimbursement_id": reimbursement.id,
            "dept_approval_id": dept_entity.id,
            "finance_approval_id": finance_entity.id,
            "ceo_approval_id": ceo_entity.id,
            "final_status": "ceo_approved",
        }

        return result


class RejectionWorkflowScenario(BaseScenario):
    """
    拒绝流程场景

    封装在某级审批被拒绝的流程
    """

    def _set_token(self):
        """设置token到API模块"""
        if self.token:
            demo_project.reimbursement.set_token(self.token)
            demo_project.dept_approval.set_token(self.token)
            demo_project.finance_approval.set_token(self.token)
            demo_project.ceo_approval.set_token(self.token)

    def execute(
        self,
        reject_at: str = "dept",  # dept, finance, ceo
        user_id: int = 1,
        amount: float = 1000.00,
        reason: str = None,
    ) -> ScenarioResult:
        """
        执行拒绝流程

        @param reject_at: 在哪一级拒绝
        @param user_id: 申请人ID
        @param amount: 报销金额
        @param reason: 报销原因
        @return: 场景执行结果
        """
        import uuid

        result = ScenarioResult()

        # 设置token
        self._set_token()

        reason = reason or f"拒绝流程测试 - {uuid.uuid4().hex[:6]}"

        # D级：创建报销申请
        create_scenario = CreateReimbursementScenario(self.token, self.factory)
        create_result = create_scenario.execute(user_id, amount, reason)

        if not create_result.success:
            result.add_error("创建报销申请失败")
            return result

        reimbursement = create_result.get_entity("reimbursement")
        result.add_entity("reimbursement", reimbursement)

        if reject_at == "dept":
            # C级拒绝
            dept_response = demo_project.dept_approval.create_dept_approval(
                reimbursement_id=reimbursement.id,
                approver_id=3,
                status="rejected",
                comment="部门审批拒绝",
            )
            if dept_response.get("code") == 200:
                dept_data = dept_response["data"]
                dept_entity = DeptApprovalEntity.from_api_response(dept_data)
                self.register_entity(dept_entity)
                result.add_entity("dept_approval", dept_entity)

        elif reject_at == "finance":
            # C级通过
            dept_response = demo_project.dept_approval.create_dept_approval(
                reimbursement_id=reimbursement.id,
                approver_id=3,
                status="approved",
                comment="部门审批通过",
            )
            if dept_response.get("code") == 200:
                dept_data = dept_response["data"]
                dept_entity = DeptApprovalEntity.from_api_response(dept_data)
                self.register_entity(dept_entity)
                result.add_entity("dept_approval", dept_entity)
            else:
                result.add_error(f"部门审批失败: {dept_response.get('message')}")
                return result

            # B级拒绝
            finance_response = demo_project.finance_approval.create_finance_approval(
                reimbursement_id=reimbursement.id,
                dept_approval_id=dept_entity.id,
                approver_id=4,
                status="rejected",
                comment="财务审批拒绝",
            )
            if finance_response.get("code") == 200:
                finance_data = finance_response["data"]
                finance_entity = FinanceApprovalEntity.from_api_response(finance_data)
                self.register_entity(finance_entity)
                result.add_entity("finance_approval", finance_entity)

        elif reject_at == "ceo":
            # C级通过
            dept_response = demo_project.dept_approval.create_dept_approval(
                reimbursement_id=reimbursement.id,
                approver_id=3,
                status="approved",
                comment="部门审批通过",
            )
            if dept_response.get("code") == 200:
                dept_data = dept_response["data"]
                dept_entity = DeptApprovalEntity.from_api_response(dept_data)
                self.register_entity(dept_entity)
                result.add_entity("dept_approval", dept_entity)
            else:
                result.add_error(f"部门审批失败: {dept_response.get('message')}")
                return result

            # B级通过
            finance_response = demo_project.finance_approval.create_finance_approval(
                reimbursement_id=reimbursement.id,
                dept_approval_id=dept_entity.id,
                approver_id=4,
                status="approved",
                comment="财务审批通过",
            )
            if finance_response.get("code") == 200:
                finance_data = finance_response["data"]
                finance_entity = FinanceApprovalEntity.from_api_response(finance_data)
                self.register_entity(finance_entity)
                result.add_entity("finance_approval", finance_entity)
            else:
                result.add_error(f"财务审批失败: {finance_response.get('message')}")
                return result

            # A级拒绝
            ceo_response = demo_project.ceo_approval.create_ceo_approval(
                reimbursement_id=reimbursement.id,
                finance_approval_id=finance_entity.id,
                approver_id=5,
                status="rejected",
                comment="总经理审批拒绝",
            )
            if ceo_response.get("code") == 200:
                ceo_data = ceo_response["data"]
                ceo_entity = CEOApprovalEntity.from_api_response(ceo_data)
                self.register_entity(ceo_entity)
                result.add_entity("ceo_approval", ceo_entity)

        result.success = True
        result.message = f"审批在{reject_at}级别被拒绝"
        result.data["rejected_at"] = reject_at
        result.data["final_status"] = f"{reject_at}_rejected"
        return result

# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 总经理审批构造器 - 使用Entity的新版本 (A级)
# @Time   : 2026-03-31
# @Author : 毛鹏
from typing import Optional, List

from ..base_builder import BaseBuilder
from ...entities.ceo_approval import CEOApprovalEntity
from ...registry import register_builder
from ....api_manager import demo_project


@register_builder("ceo_approval")
class CEOApprovalBuilder(BaseBuilder[CEOApprovalEntity]):
    """
    总经理审批构造器 - A级模块（最高层）

    依赖B级：FinanceApproval（财务审批）
    使用Entity进行数据构造和API调用
    """

    _entity_class = CEOApprovalEntity

    def __init__(self, token: str = None, factory=None):
        super().__init__(token=token, factory=factory)

    def build(
        self,
        reimbursement_id: int = 0,
        finance_approval_id: int = 0,
        approver_id: int = 5,  # 默认CEO用户ID
        status: str = "approved",
        comment: str = None,
    ) -> CEOApprovalEntity:
        """
        构造总经理审批实体（不调用API）

        @param reimbursement_id: 报销申请ID（D级）
        @param finance_approval_id: 财务审批ID（B级依赖）
        @param approver_id: 审批人ID
        @param status: 审批状态（approved/rejected）
        @param comment: 审批意见
        @return: 总经理审批实体
        """
        return CEOApprovalEntity(
            reimbursement_id=reimbursement_id,
            finance_approval_id=finance_approval_id,
            approver_id=approver_id,
            status=status,
            comment=comment
            or ("总经理审批通过" if status == "approved" else "总经理审批拒绝"),
        )

    def create(
        self, entity: CEOApprovalEntity = None, **kwargs
    ) -> Optional[CEOApprovalEntity]:
        """
        创建总经理审批（调用API）

        @param entity: 实体实例（不传则使用kwargs构造）
        @param kwargs: 构造参数
        @return: 创建后的实体
        """
        if entity is None:
            entity = self.build(**kwargs)

        if not entity.validate():
            return None

        # 设置token到API模块
        if self.token:
            demo_project.ceo_approval.set_token(self.token)

        result = demo_project.ceo_approval.create_ceo_approval(
            reimbursement_id=entity.reimbursement_id,
            finance_approval_id=entity.finance_approval_id,
            approver_id=entity.approver_id,
            status=entity.status,
            comment=entity.comment,
        )

        if result.get("code") == 200:
            data = result["data"]
            created_entity = CEOApprovalEntity.from_api_response(data)
            self._register_created(created_entity)
            return created_entity

        return None

    def get_by_id(self, approval_id: int) -> Optional[CEOApprovalEntity]:
        """
        根据ID获取总经理审批

        @param approval_id: 审批ID
        @return: 总经理审批实体
        """
        # 设置token到API模块
        if self.token:
            demo_project.ceo_approval.set_token(self.token)

        result = demo_project.ceo_approval.get_ceo_approval_by_id(approval_id)

        if result.get("code") == 200:
            data = result["data"]
            return CEOApprovalEntity.from_api_response(data)

        return None

    def update(self, entity: CEOApprovalEntity) -> Optional[CEOApprovalEntity]:
        """
        更新总经理审批

        @param entity: 实体实例
        @return: 更新后的实体
        """
        # 设置token到API模块
        if self.token:
            demo_project.ceo_approval.set_token(self.token)

        result = demo_project.ceo_approval.update_ceo_approval(
            approval_id=entity.id, **entity.to_api_payload()
        )

        if result.get("code") == 200:
            data = result["data"]
            return CEOApprovalEntity.from_api_response(data)

        return None

    def delete(self, entity: CEOApprovalEntity) -> bool:
        """
        删除总经理审批

        @param entity: 实体实例
        @return: 是否删除成功
        """
        # 设置token到API模块
        if self.token:
            demo_project.ceo_approval.set_token(self.token)

        result = demo_project.ceo_approval.delete_ceo_approval(entity.id)

        if result.get("code") == 200:
            entity.mark_as_deleted()
            return True

        return False

    def get_all(self) -> List[CEOApprovalEntity]:
        """
        获取所有总经理审批

        @return: 总经理审批实体列表
        """
        # 设置token到API模块
        if self.token:
            demo_project.ceo_approval.set_token(self.token)

        result = demo_project.ceo_approval.get_ceo_approvals()

        if result.get("code") == 200:
            data_list = result["data"]
            return [CEOApprovalEntity.from_api_response(d) for d in data_list]

        return []

    def approve(
        self,
        reimbursement_id: int,
        finance_approval_id: int,
        approver_id: int = 5,
        comment: str = "审批通过",
    ) -> Optional[CEOApprovalEntity]:
        """
        快速审批通过

        @param reimbursement_id: 报销申请ID
        @param finance_approval_id: 财务审批ID
        @param approver_id: 审批人ID
        @param comment: 审批意见
        @return: 创建的审批实体
        """
        return self.create(
            reimbursement_id=reimbursement_id,
            finance_approval_id=finance_approval_id,
            approver_id=approver_id,
            status="approved",
            comment=comment,
        )

    def reject(
        self,
        reimbursement_id: int,
        finance_approval_id: int,
        approver_id: int = 5,
        comment: str = "审批拒绝",
    ) -> Optional[CEOApprovalEntity]:
        """
        快速审批拒绝

        @param reimbursement_id: 报销申请ID
        @param finance_approval_id: 财务审批ID
        @param approver_id: 审批人ID
        @param comment: 审批意见
        @return: 创建的审批实体
        """
        return self.create(
            reimbursement_id=reimbursement_id,
            finance_approval_id=finance_approval_id,
            approver_id=approver_id,
            status="rejected",
            comment=comment,
        )

    def get_by_reimbursement(
        self, reimbursement_id: int
    ) -> Optional[CEOApprovalEntity]:
        """
        根据报销申请ID获取CEO审批

        @param reimbursement_id: 报销申请ID
        @return: CEO审批实体
        """
        approvals = self.get_all()
        for approval in approvals:
            if approval.reimbursement_id == reimbursement_id:
                return approval
        return None

    def can_create(self, reimbursement_id: int) -> bool:
        """
        检查是否可以为指定报销申请创建CEO审批

        @param reimbursement_id: 报销申请ID
        @return: 是否可以创建
        """
        # 检查是否已存在CEO审批
        existing = self.get_by_reimbursement(reimbursement_id)
        return existing is None

    def get_workflow(self, reimbursement_id: int) -> Optional[dict]:
        """
        获取完整审批流程信息

        @param reimbursement_id: 报销申请ID
        @return: 包含所有审批信息的字典
        """
        from ...entities.reimbursement import ReimbursementEntity
        from ...entities.dept_approval import DeptApprovalEntity
        from ...entities.finance_approval import FinanceApprovalEntity

        # 获取报销申请
        reimbursement_result = demo_project.reimbursement.get_reimbursement_by_id(
            reimbursement_id
        )
        if reimbursement_result.get("code") != 200:
            return None
        reimbursement = ReimbursementEntity.from_api_response(
            reimbursement_result["data"]
        )

        # 获取部门审批
        dept_approvals = self._get_all_by_reimbursement(reimbursement_id, "dept")
        dept_approval = dept_approvals[0] if dept_approvals else None

        # 获取财务审批
        finance_approvals = self._get_all_by_reimbursement(reimbursement_id, "finance")
        finance_approval = finance_approvals[0] if finance_approvals else None

        # 获取CEO审批
        ceo_approvals = self._get_all_by_reimbursement(reimbursement_id, "ceo")
        ceo_approval = ceo_approvals[0] if ceo_approvals else None

        return {
            "reimbursement": reimbursement.__dict__ if reimbursement else None,
            "dept_approval": dept_approval.__dict__ if dept_approval else None,
            "finance_approval": finance_approval.__dict__ if finance_approval else None,
            "ceo_approval": ceo_approval.__dict__ if ceo_approval else None,
        }

    def _get_all_by_reimbursement(
        self, reimbursement_id: int, approval_type: str
    ) -> list:
        """根据报销申请ID获取所有相关审批"""
        if approval_type == "dept":
            result = demo_project.dept_approval.get_dept_approvals()
            if result.get("code") == 200:
                from ...entities.dept_approval import DeptApprovalEntity

                approvals = [
                    DeptApprovalEntity.from_api_response(d) for d in result["data"]
                ]
                return [a for a in approvals if a.reimbursement_id == reimbursement_id]
        elif approval_type == "finance":
            result = demo_project.finance_approval.get_finance_approvals()
            if result.get("code") == 200:
                from ...entities.finance_approval import FinanceApprovalEntity

                approvals = [
                    FinanceApprovalEntity.from_api_response(d) for d in result["data"]
                ]
                return [a for a in approvals if a.reimbursement_id == reimbursement_id]
        elif approval_type == "ceo":
            result = demo_project.ceo_approval.get_ceo_approvals()
            if result.get("code") == 200:
                approvals = [
                    self._entity_class.from_api_response(d) for d in result["data"]
                ]
                return [a for a in approvals if a.reimbursement_id == reimbursement_id]
        return []

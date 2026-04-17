# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 财务审批构造器 - 使用Entity的新版本 (B级)
# @Time   : 2026-03-31
# @Author : 毛鹏
from typing import Optional, List

from core.base import BaseBuilder
from ...entities.finance_approval import FinanceApprovalEntity
from ...registry import register_builder
from ....api_manager import pytest_api_mock


@register_builder("finance_approval")
class FinanceApprovalBuilder(BaseBuilder[FinanceApprovalEntity]):
    """
    财务审批构造器 - B级模块

    依赖C级：DeptApproval（部门审批）
    使用Entity进行数据构造和API调用
    """

    def __init__(self, token: str = None, factory=None):
        super().__init__(token=token, factory=factory)

    def build(
            self,
            reimbursement_id: int = 0,
            dept_approval_id: int = 0,
            approver_id: int = 4,  # 默认财务经理用户ID
            status: str = "approved",
            comment: str = None,
    ) -> FinanceApprovalEntity:
        """
        构造财务审批实体（不调用API）

        @param reimbursement_id: 报销申请ID（D级）
        @param dept_approval_id: 部门审批ID（C级依赖）
        @param approver_id: 审批人ID
        @param status: 审批状态（approved/rejected）
        @param comment: 审批意见
        @return: 财务审批实体
        """
        return FinanceApprovalEntity(
            reimbursement_id=reimbursement_id,
            dept_approval_id=dept_approval_id,
            approver_id=approver_id,
            status=status,
            comment=comment
                    or ("财务审批通过" if status == "approved" else "财务审批拒绝"),
        )

    def create(
            self, entity: FinanceApprovalEntity = None, **kwargs
    ) -> Optional[FinanceApprovalEntity]:
        """
        创建财务审批（调用API）

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
            pytest_api_mock.finance_approval.set_token(self.token)

        result = pytest_api_mock.finance_approval.create_finance_approval(
            reimbursement_id=entity.reimbursement_id,
            dept_approval_id=entity.dept_approval_id,
            approver_id=entity.approver_id,
            status=entity.status,
            comment=entity.comment,
        )

        if result.get("code") == 200:
            data = result["data"]
            created_entity = FinanceApprovalEntity.from_api_response(data)
            self._register_created(created_entity)
            return created_entity

        return None

    def get_by_id(self, approval_id: int) -> Optional[FinanceApprovalEntity]:
        """
        根据ID获取财务审批

        @param approval_id: 审批ID
        @return: 财务审批实体
        """
        # 设置token到API模块
        if self.token:
            pytest_api_mock.finance_approval.set_token(self.token)

        result = pytest_api_mock.finance_approval.get_finance_approval_by_id(approval_id)

        if result.get("code") == 200:
            data = result["data"]
            return FinanceApprovalEntity.from_api_response(data)

        return None

    def update(self, entity: FinanceApprovalEntity) -> Optional[FinanceApprovalEntity]:
        """
        更新财务审批

        @param entity: 实体实例
        @return: 更新后的实体
        """
        # 设置token到API模块
        if self.token:
            pytest_api_mock.finance_approval.set_token(self.token)

        result = pytest_api_mock.finance_approval.update_finance_approval(
            approval_id=entity.id, **entity.to_api_payload()
        )

        if result.get("code") == 200:
            data = result["data"]
            return FinanceApprovalEntity.from_api_response(data)

        return None

    def delete(self, entity: FinanceApprovalEntity) -> bool:
        """
        删除财务审批

        @param entity: 实体实例
        @return: 是否删除成功
        """
        # 设置token到API模块
        if self.token:
            pytest_api_mock.finance_approval.set_token(self.token)

        result = pytest_api_mock.finance_approval.delete_finance_approval(entity.id)

        if result.get("code") == 200:
            entity.mark_as_deleted()
            return True

        return False

    def get_all(self) -> List[FinanceApprovalEntity]:
        """
        获取所有财务审批

        @return: 财务审批实体列表
        """
        # 设置token到API模块
        if self.token:
            pytest_api_mock.finance_approval.set_token(self.token)

        result = pytest_api_mock.finance_approval.get_finance_approvals()

        if result.get("code") == 200:
            data_list = result["data"]
            return [FinanceApprovalEntity.from_api_response(d) for d in data_list]

        return []

    def approve(
            self,
            reimbursement_id: int,
            dept_approval_id: int,
            approver_id: int = 4,
            comment: str = "审批通过",
    ) -> Optional[FinanceApprovalEntity]:
        """
        快速审批通过

        @param reimbursement_id: 报销申请ID
        @param dept_approval_id: 部门审批ID
        @param approver_id: 审批人ID
        @param comment: 审批意见
        @return: 创建的审批实体
        """
        return self.create(
            reimbursement_id=reimbursement_id,
            dept_approval_id=dept_approval_id,
            approver_id=approver_id,
            status="approved",
            comment=comment,
        )

    def reject(
            self,
            reimbursement_id: int,
            dept_approval_id: int,
            approver_id: int = 4,
            comment: str = "审批拒绝",
    ) -> Optional[FinanceApprovalEntity]:
        """
        快速审批拒绝

        @param reimbursement_id: 报销申请ID
        @param dept_approval_id: 部门审批ID
        @param approver_id: 审批人ID
        @param comment: 审批意见
        @return: 创建的审批实体
        """
        return self.create(
            reimbursement_id=reimbursement_id,
            dept_approval_id=dept_approval_id,
            approver_id=approver_id,
            status="rejected",
            comment=comment,
        )

    def get_by_reimbursement(
            self, reimbursement_id: int
    ) -> Optional[FinanceApprovalEntity]:
        """
        根据报销申请ID获取财务审批

        @param reimbursement_id: 报销申请ID
        @return: 财务审批实体
        """
        approvals = self.get_all()
        for approval in approvals:
            if approval.reimbursement_id == reimbursement_id:
                return approval
        return None

    def can_create(self, reimbursement_id: int) -> bool:
        """
        检查是否可以为指定报销申请创建财务审批

        @param reimbursement_id: 报销申请ID
        @return: 是否可以创建
        """
        # 检查是否已存在财务审批
        existing = self.get_by_reimbursement(reimbursement_id)
        return existing is None

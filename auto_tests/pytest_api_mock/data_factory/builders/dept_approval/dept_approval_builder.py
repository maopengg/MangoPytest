# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 部门审批构造器 - 使用Entity的新版本 (C级)
# @Time   : 2026-03-31
# @Author : 毛鹏
from typing import Optional, List

from core.base import BaseBuilder
from ...entities.dept_approval import DeptApprovalEntity
from ...registry import register_builder
from ....api_manager import demo_project


@register_builder("dept_approval")
class DeptApprovalBuilder(BaseBuilder[DeptApprovalEntity]):
    """
    部门审批构造器 - C级模块

    依赖D级：Reimbursement（报销申请）
    使用Entity进行数据构造和API调用
    """

    def __init__(self, token: str = None, factory=None):
        super().__init__(token=token, factory=factory)

    def build(
            self,
            reimbursement_id: int = 0,
            approver_id: int = 3,  # 默认部门经理用户ID
            status: str = "approved",
            comment: str = None,
    ) -> DeptApprovalEntity:
        """
        构造部门审批实体（不调用API）

        @param reimbursement_id: 报销申请ID（D级依赖）
        @param approver_id: 审批人ID
        @param status: 审批状态（approved/rejected）
        @param comment: 审批意见
        @return: 部门审批实体
        """
        return DeptApprovalEntity(
            reimbursement_id=reimbursement_id,
            approver_id=approver_id,
            status=status,
            comment=comment or ("审批通过" if status == "approved" else "审批拒绝"),
        )

    def create(
            self, entity: DeptApprovalEntity = None, **kwargs
    ) -> Optional[DeptApprovalEntity]:
        """
        创建部门审批（调用API）

        @param entity: 实体实例（不传则使用kwargs构造）
        @param kwargs: 构造参数
        @return: 创建后的实体
        """
        if entity is None:
            entity = self.build(**kwargs)

        # 验证实体数据
        if not entity.validate():
            print(
                f"[DeptApprovalBuilder] 实体验证失败: reimbursement_id={entity.reimbursement_id}, approver_id={entity.approver_id}, status={entity.status}")
            return None

        # 设置token到API模块
        if self.token:
            demo_project.dept_approval.set_token(self.token)

        result = demo_project.dept_approval.create_dept_approval(
            reimbursement_id=entity.reimbursement_id,
            approver_id=entity.approver_id,
            status=entity.status,
            comment=entity.comment,
        )

        print(f"[DeptApprovalBuilder] API返回结果: {result}")

        if result.get("code") == 200:
            data = result.get("data")
            if data:
                created_entity = DeptApprovalEntity.from_api_response(data)
                self._register_created(created_entity)
                return created_entity
            else:
                print(f"[DeptApprovalBuilder] API返回数据为空")
        else:
            print(f"[DeptApprovalBuilder] API调用失败: code={result.get('code')}, message={result.get('message')}")

        return None

    def get_by_id(self, approval_id: int) -> Optional[DeptApprovalEntity]:
        """
        根据ID获取部门审批

        @param approval_id: 审批ID
        @return: 部门审批实体
        """
        # 设置token到API模块
        if self.token:
            demo_project.dept_approval.set_token(self.token)

        result = demo_project.dept_approval.get_dept_approval_by_id(approval_id)

        if result.get("code") == 200:
            data = result["data"]
            return DeptApprovalEntity.from_api_response(data)

        return None

    def update(self, entity: DeptApprovalEntity) -> Optional[DeptApprovalEntity]:
        """
        更新部门审批

        @param entity: 实体实例
        @return: 更新后的实体
        """
        # 设置token到API模块
        if self.token:
            demo_project.dept_approval.set_token(self.token)

        result = demo_project.dept_approval.update_dept_approval(
            approval_id=entity.id, **entity.to_api_payload()
        )

        if result.get("code") == 200:
            data = result["data"]
            return DeptApprovalEntity.from_api_response(data)

        return None

    def delete(self, entity: DeptApprovalEntity) -> bool:
        """
        删除部门审批

        @param entity: 实体实例
        @return: 是否删除成功
        """
        # 设置token到API模块
        if self.token:
            demo_project.dept_approval.set_token(self.token)

        result = demo_project.dept_approval.delete_dept_approval(entity.id)

        if result.get("code") == 200:
            entity.mark_as_deleted()
            return True

        return False

    def get_all(self) -> List[DeptApprovalEntity]:
        """
        获取所有部门审批

        @return: 部门审批实体列表
        """
        # 设置token到API模块
        if self.token:
            demo_project.dept_approval.set_token(self.token)

        result = demo_project.dept_approval.get_dept_approvals()

        if result.get("code") == 200:
            data_list = result["data"]
            return [DeptApprovalEntity.from_api_response(d) for d in data_list]

        return []

    def approve(
            self, reimbursement_id: int, approver_id: int = 3, comment: str = "审批通过"
    ) -> Optional[DeptApprovalEntity]:
        """
        快速审批通过

        @param reimbursement_id: 报销申请ID
        @param approver_id: 审批人ID
        @param comment: 审批意见
        @return: 创建的审批实体
        """
        return self.create(
            reimbursement_id=reimbursement_id,
            approver_id=approver_id,
            status="approved",
            comment=comment,
        )

    def reject(
            self, reimbursement_id: int, approver_id: int = 3, comment: str = "审批拒绝"
    ) -> Optional[DeptApprovalEntity]:
        """
        快速审批拒绝

        @param reimbursement_id: 报销申请ID
        @param approver_id: 审批人ID
        @param comment: 审批意见
        @return: 创建的审批实体
        """
        return self.create(
            reimbursement_id=reimbursement_id,
            approver_id=approver_id,
            status="rejected",
            comment=comment,
        )

    def get_by_reimbursement(
            self, reimbursement_id: int
    ) -> Optional[DeptApprovalEntity]:
        """
        根据报销申请ID获取部门审批

        @param reimbursement_id: 报销申请ID
        @return: 部门审批实体
        """
        approvals = self.get_all()
        for approval in approvals:
            if approval.reimbursement_id == reimbursement_id:
                return approval
        return None

    def can_create(self, reimbursement_id: int) -> bool:
        """
        检查是否可以为指定报销申请创建部门审批

        @param reimbursement_id: 报销申请ID
        @return: 是否可以创建
        """
        # 检查是否已存在部门审批
        existing = self.get_by_reimbursement(reimbursement_id)
        return existing is None

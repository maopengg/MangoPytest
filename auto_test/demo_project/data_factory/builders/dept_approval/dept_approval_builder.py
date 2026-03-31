# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 部门审批构造器 - C级模块 (依赖D级)
# @Time   : 2026-03-31
# @Author : 毛鹏
from typing import Dict, Any, List, Optional

from ..base_builder import BaseBuilder
from auto_test.demo_project.api_manager import demo_project
from ...registry import register_builder


@register_builder("dept_approval")
class DeptApprovalBuilder(BaseBuilder):
    """
    部门审批构造器 - C级模块
    对应 /dept-approvals 接口
    依赖D级：Reimbursement（报销申请）
    """

    def __init__(self, token: str = None, factory=None):
        super().__init__(token, factory)
        self._dept_manager_id = 3  # 部门经理用户ID

    def build(self, reimbursement_id: int, approver_id: int = None,
              status: str = "approved", comment: str = None) -> Dict[str, Any]:
        """
        构造部门审批数据（不调用API）
        @param reimbursement_id: 报销申请ID（D级依赖）
        @param approver_id: 审批人ID
        @param status: 审批状态（approved/rejected）
        @param comment: 审批意见
        @return: 部门审批数据字典
        """
        return {
            "reimbursement_id": reimbursement_id,
            "approver_id": approver_id or self._dept_manager_id,
            "status": status,
            "comment": comment or ("同意" if status == "approved" else "拒绝")
        }

    def create(self, reimbursement_id: int, approver_id: int = None,
               status: str = "approved", comment: str = None) -> Dict[str, Any]:
        """
        创建部门审批（调用API）
        依赖：D级报销申请必须存在且状态为pending
        @return: 创建的部门审批数据
        """
        approval_data = self.build(reimbursement_id, approver_id, status, comment)

        api_data = self._create_api_data(
            url="/dept-approvals",
            method="POST",
            json_data=approval_data
        )

        result = demo_project.dept_approval.create_dept_approval(api_data)
        if result.response and result.response.json().get("code") == 200:
            created_approval = result.response.json()["data"]
            self._register_created(created_approval)
            return created_approval
        return None

    def get_all(self, reimbursement_id: int = None) -> List[Dict[str, Any]]:
        """
        获取部门审批列表
        @param reimbursement_id: 可选，按报销申请ID筛选
        @return: 部门审批列表
        """
        params = {}
        if reimbursement_id:
            params["reimbursement_id"] = reimbursement_id

        api_data = self._create_api_data(
            url="/dept-approvals",
            method="GET",
            params=params
        )

        result = demo_project.dept_approval.get_dept_approvals(api_data)
        if result.response and result.response.json().get("code") == 200:
            return result.response.json()["data"]
        return []

    def get_by_reimbursement(self, reimbursement_id: int) -> Optional[Dict[str, Any]]:
        """
        根据报销申请ID获取部门审批
        @param reimbursement_id: 报销申请ID
        @return: 部门审批数据
        """
        approvals = self.get_all(reimbursement_id)
        if approvals:
            return approvals[0]
        return None

    def update(self, approval_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新部门审批
        @param approval_id: 审批ID
        @param data: 更新数据
        @return: 更新后的部门审批数据
        """
        api_data = self._create_api_data(
            url="/dept-approvals",
            method="PUT",
            params={"approval_id": approval_id},
            json_data=data
        )

        result = demo_project.dept_approval.update_dept_approval(api_data)
        if result.response and result.response.json().get("code") == 200:
            return result.response.json()["data"]
        return None

    def approve(self, reimbursement_id: int, approver_id: int = None,
                comment: str = "同意") -> Dict[str, Any]:
        """
        快捷方法：通过部门审批
        @param reimbursement_id: 报销申请ID
        @param approver_id: 审批人ID
        @param comment: 审批意见
        @return: 创建的部门审批数据
        """
        return self.create(reimbursement_id, approver_id, "approved", comment)

    def reject(self, reimbursement_id: int, approver_id: int = None,
               comment: str = "拒绝") -> Dict[str, Any]:
        """
        快捷方法：拒绝部门审批
        @param reimbursement_id: 报销申请ID
        @param approver_id: 审批人ID
        @param comment: 审批意见
        @return: 创建的部门审批数据
        """
        return self.create(reimbursement_id, approver_id, "rejected", comment)

    def can_create(self, reimbursement_id: int) -> bool:
        """
        检查是否可以创建部门审批
        条件：报销申请存在且状态为pending
        @param reimbursement_id: 报销申请ID
        @return: 是否可以创建
        """
        from ..reimbursement import ReimbursementBuilder
        reimbursement_builder = ReimbursementBuilder(self.token, self.factory)
        return reimbursement_builder.is_pending(reimbursement_id)

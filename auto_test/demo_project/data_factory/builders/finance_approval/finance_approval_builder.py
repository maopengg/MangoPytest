# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 财务审批构造器 - B级模块 (依赖C级)
# @Time   : 2026-03-31
# @Author : 毛鹏
from typing import Dict, Any, List, Optional

from ..base_builder import BaseBuilder
from auto_test.demo_project.api_manager import demo_project
from ...registry import register_builder


@register_builder("finance_approval")
class FinanceApprovalBuilder(BaseBuilder):
    """
    财务审批构造器 - B级模块
    对应 /finance-approvals 接口
    依赖C级：DeptApproval（部门审批）必须已通过
    """

    def __init__(self, token: str = None, factory=None):
        super().__init__(token, factory)
        self._finance_manager_id = 4  # 财务经理用户ID

    def build(self, reimbursement_id: int, dept_approval_id: int,
              approver_id: int = None, status: str = "approved",
              comment: str = None) -> Dict[str, Any]:
        """
        构造财务审批数据（不调用API）
        @param reimbursement_id: 报销申请ID（D级）
        @param dept_approval_id: 部门审批ID（C级依赖）
        @param approver_id: 审批人ID
        @param status: 审批状态（approved/rejected）
        @param comment: 审批意见
        @return: 财务审批数据字典
        """
        return {
            "reimbursement_id": reimbursement_id,
            "dept_approval_id": dept_approval_id,
            "approver_id": approver_id or self._finance_manager_id,
            "status": status,
            "comment": comment or ("财务审核通过" if status == "approved" else "财务审核不通过")
        }

    def create(self, reimbursement_id: int, dept_approval_id: int,
               approver_id: int = None, status: str = "approved",
               comment: str = None) -> Dict[str, Any]:
        """
        创建财务审批（调用API）
        依赖：C级部门审批必须通过
        @return: 创建的财务审批数据
        """
        approval_data = self.build(reimbursement_id, dept_approval_id, approver_id, status, comment)

        api_data = self._create_api_data(
            url="/finance-approvals",
            method="POST",
            json_data=approval_data
        )

        result = demo_project.finance_approval.create_finance_approval(api_data)
        if result.response and result.response.json().get("code") == 200:
            created_approval = result.response.json()["data"]
            self._register_created(created_approval)
            return created_approval
        return None

    def get_all(self, reimbursement_id: int = None) -> List[Dict[str, Any]]:
        """
        获取财务审批列表
        @param reimbursement_id: 可选，按报销申请ID筛选
        @return: 财务审批列表
        """
        params = {}
        if reimbursement_id:
            params["reimbursement_id"] = reimbursement_id

        api_data = self._create_api_data(
            url="/finance-approvals",
            method="GET",
            params=params
        )

        result = demo_project.finance_approval.get_finance_approvals(api_data)
        if result.response and result.response.json().get("code") == 200:
            return result.response.json()["data"]
        return []

    def get_by_reimbursement(self, reimbursement_id: int) -> Optional[Dict[str, Any]]:
        """
        根据报销申请ID获取财务审批
        @param reimbursement_id: 报销申请ID
        @return: 财务审批数据
        """
        approvals = self.get_all(reimbursement_id)
        if approvals:
            return approvals[0]
        return None

    def update(self, approval_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新财务审批
        @param approval_id: 审批ID
        @param data: 更新数据
        @return: 更新后的财务审批数据
        """
        api_data = self._create_api_data(
            url="/finance-approvals",
            method="PUT",
            params={"approval_id": approval_id},
            json_data=data
        )

        result = demo_project.finance_approval.update_finance_approval(api_data)
        if result.response and result.response.json().get("code") == 200:
            return result.response.json()["data"]
        return None

    def approve(self, reimbursement_id: int, dept_approval_id: int,
                approver_id: int = None, comment: str = "财务审核通过") -> Dict[str, Any]:
        """
        快捷方法：通过财务审批
        @param reimbursement_id: 报销申请ID
        @param dept_approval_id: 部门审批ID
        @param approver_id: 审批人ID
        @param comment: 审批意见
        @return: 创建的财务审批数据
        """
        return self.create(reimbursement_id, dept_approval_id, approver_id, "approved", comment)

    def reject(self, reimbursement_id: int, dept_approval_id: int,
               approver_id: int = None, comment: str = "财务审核不通过") -> Dict[str, Any]:
        """
        快捷方法：拒绝财务审批
        @param reimbursement_id: 报销申请ID
        @param dept_approval_id: 部门审批ID
        @param approver_id: 审批人ID
        @param comment: 审批意见
        @return: 创建的财务审批数据
        """
        return self.create(reimbursement_id, dept_approval_id, approver_id, "rejected", comment)

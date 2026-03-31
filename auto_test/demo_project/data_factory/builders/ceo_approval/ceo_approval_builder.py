# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 总经理审批构造器 - A级模块 (依赖B级)
# @Time   : 2026-03-31
# @Author : 毛鹏
from typing import Dict, Any, List, Optional

from ..base_builder import BaseBuilder
from auto_test.demo_project.api_manager import demo_project
from ...registry import register_builder


@register_builder("ceo_approval")
class CEOApprovalBuilder(BaseBuilder):
    """
    总经理审批构造器 - A级模块 (最高层)
    对应 /ceo-approvals 接口
    依赖B级：FinanceApproval（财务审批）必须已通过
    """

    def __init__(self, token: str = None, factory=None):
        super().__init__(token, factory)
        self._ceo_id = 5  # CEO用户ID

    def build(self, reimbursement_id: int, finance_approval_id: int,
              approver_id: int = None, status: str = "approved",
              comment: str = None) -> Dict[str, Any]:
        """
        构造总经理审批数据（不调用API）
        @param reimbursement_id: 报销申请ID（D级）
        @param finance_approval_id: 财务审批ID（B级依赖）
        @param approver_id: 审批人ID
        @param status: 审批状态（approved/rejected）
        @param comment: 审批意见
        @return: 总经理审批数据字典
        """
        return {
            "reimbursement_id": reimbursement_id,
            "finance_approval_id": finance_approval_id,
            "approver_id": approver_id or self._ceo_id,
            "status": status,
            "comment": comment or ("总经理批准" if status == "approved" else "总经理否决")
        }

    def create(self, reimbursement_id: int, finance_approval_id: int,
               approver_id: int = None, status: str = "approved",
               comment: str = None) -> Dict[str, Any]:
        """
        创建总经理审批（调用API）
        依赖：B级财务审批必须通过
        @return: 创建的总经理审批数据
        """
        approval_data = self.build(reimbursement_id, finance_approval_id, approver_id, status, comment)

        api_data = self._create_api_data(
            url="/ceo-approvals",
            method="POST",
            json_data=approval_data
        )

        result = demo_project.ceo_approval.create_ceo_approval(api_data)
        if result.response and result.response.json().get("code") == 200:
            created_approval = result.response.json()["data"]
            self._register_created(created_approval)
            return created_approval
        return None

    def get_all(self, reimbursement_id: int = None) -> List[Dict[str, Any]]:
        """
        获取总经理审批列表
        @param reimbursement_id: 可选，按报销申请ID筛选
        @return: 总经理审批列表
        """
        params = {}
        if reimbursement_id:
            params["reimbursement_id"] = reimbursement_id

        api_data = self._create_api_data(
            url="/ceo-approvals",
            method="GET",
            params=params
        )

        result = demo_project.ceo_approval.get_ceo_approvals(api_data)
        if result.response and result.response.json().get("code") == 200:
            return result.response.json()["data"]
        return []

    def get_by_reimbursement(self, reimbursement_id: int) -> Optional[Dict[str, Any]]:
        """
        根据报销申请ID获取总经理审批
        @param reimbursement_id: 报销申请ID
        @return: 总经理审批数据
        """
        approvals = self.get_all(reimbursement_id)
        if approvals:
            return approvals[0]
        return None

    def get_workflow(self, reimbursement_id: int) -> Dict[str, Any]:
        """
        获取完整的审批流程信息
        @param reimbursement_id: 报销申请ID
        @return: 完整流程数据
        """
        api_data = self._create_api_data(
            url="/workflow",
            method="GET",
            params={"reimbursement_id": reimbursement_id}
        )

        result = demo_project.ceo_approval.get_workflow(api_data)
        if result.response and result.response.json().get("code") == 200:
            return result.response.json()["data"]
        return {}

    def approve(self, reimbursement_id: int, finance_approval_id: int,
                approver_id: int = None, comment: str = "总经理批准") -> Dict[str, Any]:
        """
        快捷方法：通过总经理审批
        @param reimbursement_id: 报销申请ID
        @param finance_approval_id: 财务审批ID
        @param approver_id: 审批人ID
        @param comment: 审批意见
        @return: 创建的总经理审批数据
        """
        return self.create(reimbursement_id, finance_approval_id, approver_id, "approved", comment)

    def reject(self, reimbursement_id: int, finance_approval_id: int,
               approver_id: int = None, comment: str = "总经理否决") -> Dict[str, Any]:
        """
        快捷方法：拒绝总经理审批
        @param reimbursement_id: 报销申请ID
        @param finance_approval_id: 财务审批ID
        @param approver_id: 审批人ID
        @param comment: 审批意见
        @return: 创建的总经理审批数据
        """
        return self.create(reimbursement_id, finance_approval_id, approver_id, "rejected", comment)

    def is_fully_approved(self, reimbursement_id: int) -> bool:
        """
        检查报销申请是否已完成全部审批流程
        @param reimbursement_id: 报销申请ID
        @return: 是否已完成全部审批
        """
        workflow = self.get_workflow(reimbursement_id)
        if workflow:
            reimbursement = workflow.get("reimbursement", {})
            return reimbursement.get("status") == "ceo_approved"
        return False

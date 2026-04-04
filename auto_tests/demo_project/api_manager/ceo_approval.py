# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 总经理审批API - 使用 Core APIClient
# @Time   : 2024-03-17 19:50
# @Author : 毛鹏

from core.base import BaseAPI


class CEOApprovalAPI(BaseAPI):
    """总经理审批API - 对应 /ceo-approvals 接口"""

    def get_ceo_approvals(self) -> dict:
        """
        获取总经理审批列表
        GET /ceo-approvals
        @return: 响应字典
        """
        response = self.client.get("/ceo-approvals")
        return response.data

    def get_ceo_approval_by_id(self, approval_id: int) -> dict:
        """
        根据ID获取总经理审批
        GET /ceo-approvals?id={approval_id}
        @param approval_id: 审批ID
        @return: 响应字典
        """
        response = self.client.get("/ceo-approvals", params={"id": approval_id})
        return response.data

    def create_ceo_approval(
            self,
            reimbursement_id: int,
            finance_approval_id: int,
            approver_id: int,
            status: str,
            comment: str = None,
    ) -> dict:
        """
        创建总经理审批
        POST /ceo-approvals
        @param reimbursement_id: 报销申请ID
        @param finance_approval_id: 财务审批ID
        @param approver_id: 审批人ID
        @param status: 审批状态（approved/rejected）
        @param comment: 审批意见
        @return: 响应字典
        """
        data = {
            "reimbursement_id": reimbursement_id,
            "finance_approval_id": finance_approval_id,
            "approver_id": approver_id,
            "status": status,
        }
        if comment:
            data["comment"] = comment
        response = self.client.post("/ceo-approvals", json=data)
        return response.data

    def update_ceo_approval(self, approval_id: int, **kwargs) -> dict:
        """
        更新总经理审批
        PUT /ceo-approvals?approval_id={approval_id}
        @param approval_id: 审批ID
        @param kwargs: 更新字段
        @return: 响应字典
        """
        response = self.client.put("/ceo-approvals", json=kwargs, params={"approval_id": approval_id})
        return response.data

    def delete_ceo_approval(self, approval_id: int) -> dict:
        """
        删除总经理审批
        DELETE /ceo-approvals?approval_id={approval_id}
        @param approval_id: 审批ID
        @return: 响应字典
        """
        response = self.client.delete("/ceo-approvals", params={"approval_id": approval_id})
        return response.data

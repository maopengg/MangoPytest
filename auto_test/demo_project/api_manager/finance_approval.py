# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 财务审批API - 使用 Core APIClient
# @Time   : 2024-03-17 19:50
# @Author : 毛鹏

from auto_test.demo_project.core.api.client import APIClient


class FinanceApprovalAPI:
    """财务审批API - 对应 /finance-approvals 接口"""

    def __init__(self):
        self._client = APIClient(base_url="http://localhost:8003")

    def set_host(self, host: str):
        """设置API服务器地址"""
        self._client.set_base_url(host)

    def set_token(self, token: str):
        """设置认证token"""
        self._client.set_auth_token(token)

    def get_finance_approvals(self) -> dict:
        """
        获取财务审批列表
        GET /finance-approvals
        @return: 响应字典
        """
        response = self._client.get("/finance-approvals")
        return response.data

    def get_finance_approval_by_id(self, approval_id: int) -> dict:
        """
        根据ID获取财务审批
        GET /finance-approvals?id={approval_id}
        @param approval_id: 审批ID
        @return: 响应字典
        """
        response = self._client.get("/finance-approvals", params={"id": approval_id})
        return response.data

    def create_finance_approval(self, reimbursement_id: int, dept_approval_id: int, approver_id: int, status: str,
                                comment: str = None) -> dict:
        """
        创建财务审批
        POST /finance-approvals
        @param reimbursement_id: 报销申请ID
        @param dept_approval_id: 部门审批ID
        @param approver_id: 审批人ID
        @param status: 审批状态（approved/rejected）
        @param comment: 审批意见
        @return: 响应字典
        """
        data = {
            "reimbursement_id": reimbursement_id,
            "dept_approval_id": dept_approval_id,
            "approver_id": approver_id,
            "status": status
        }
        if comment:
            data["comment"] = comment
        response = self._client.post("/finance-approvals", data=data)
        return response.data

    def update_finance_approval(self, approval_id: int, **kwargs) -> dict:
        """
        更新财务审批
        PUT /finance-approvals?approval_id={approval_id}
        @param approval_id: 审批ID
        @param kwargs: 更新字段
        @return: 响应字典
        """
        response = self._client.put("/finance-approvals", data=kwargs, params={"approval_id": approval_id})
        return response.data

    def delete_finance_approval(self, approval_id: int) -> dict:
        """
        删除财务审批
        DELETE /finance-approvals?approval_id={approval_id}
        @param approval_id: 审批ID
        @return: 响应字典
        """
        response = self._client.delete("/finance-approvals", params={"approval_id": approval_id})
        return response.data

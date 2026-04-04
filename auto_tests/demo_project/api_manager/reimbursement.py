# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 报销申请API - 使用 Core APIClient
# @Time   : 2024-03-17 19:50
# @Author : 毛鹏

from core.api.client import APIClient


class ReimbursementAPI:
    """报销申请API - 对应 /reimbursements 接口"""

    def __init__(self):
        self._client = APIClient(base_url="http://localhost:8003")

    def set_host(self, host: str):
        """设置API服务器地址"""
        self._client.set_base_url(host)

    def set_token(self, token: str):
        """设置认证token"""
        self._client.set_auth_token(token)

    def get_reimbursements(self) -> dict:
        """
        获取报销申请列表
        GET /reimbursements
        @return: 响应字典
        """
        response = self._client.get("/reimbursements")
        return response.data

    def get_reimbursement_by_id(self, reimbursement_id: int) -> dict:
        """
        根据ID获取报销申请
        GET /reimbursements?id={reimbursement_id}
        @param reimbursement_id: 报销申请ID
        @return: 响应字典
        """
        response = self._client.get("/reimbursements", params={"id": reimbursement_id})
        return response.data

    def create_reimbursement(self, user_id: int, amount: float, reason: str) -> dict:
        """
        创建报销申请
        POST /reimbursements
        @param user_id: 用户ID
        @param amount: 报销金额
        @param reason: 报销原因
        @return: 响应字典
        """
        response = self._client.post(
            "/reimbursements",
            data={"user_id": user_id, "amount": amount, "reason": reason}
        )
        return response.data

    def update_reimbursement(self, reimbursement_id: int, **kwargs) -> dict:
        """
        更新报销申请
        PUT /reimbursements/{reimbursement_id}
        @param reimbursement_id: 报销申请ID
        @param kwargs: 更新字段
        @return: 响应字典
        """
        response = self._client.put(f"/reimbursements/{reimbursement_id}", data=kwargs)
        return response.data

    def delete_reimbursement(self, reimbursement_id: int) -> dict:
        """
        删除报销申请
        DELETE /reimbursements/{reimbursement_id}
        @param reimbursement_id: 报销申请ID
        @return: 响应字典
        """
        response = self._client.delete(f"/reimbursements/{reimbursement_id}")
        return response.data

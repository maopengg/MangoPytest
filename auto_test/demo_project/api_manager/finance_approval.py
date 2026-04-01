# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-03-17 19:50
# @Author : 毛鹏
from urllib.parse import urljoin

import requests


class FinanceApprovalAPI:
    """财务审批API - 对应 /finance-approvals 接口"""

    def __init__(self):
        self._host = "http://localhost:8003"
        self._token = None

    def set_host(self, host: str):
        """设置API服务器地址"""
        self._host = host.rstrip('/')

    def set_token(self, token: str):
        """设置认证token"""
        self._token = token

    def _get_url(self, path: str) -> str:
        """获取完整URL"""
        return urljoin(self._host + "/", path)

    def _get_headers(self) -> dict:
        """获取请求头"""
        headers = {}
        if self._token:
            headers["X-Token"] = self._token
        return headers

    def get_finance_approvals(self) -> dict:
        """
        获取财务审批列表
        GET /finance-approvals
        @return: 响应字典
        """
        url = self._get_url("finance-approvals")
        response = requests.get(url, headers=self._get_headers())
        return response.json()

    def get_finance_approval_by_id(self, approval_id: int) -> dict:
        """
        根据ID获取财务审批
        GET /finance-approvals?id={approval_id}
        @param approval_id: 审批ID
        @return: 响应字典
        """
        url = self._get_url("finance-approvals")
        response = requests.get(url, params={"id": approval_id}, headers=self._get_headers())
        return response.json()

    def create_finance_approval(self, reimbursement_id: int, dept_approval_id: int, approver_id: int, status: str, comment: str = None) -> dict:
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
        url = self._get_url("finance-approvals")
        data = {
            "reimbursement_id": reimbursement_id,
            "dept_approval_id": dept_approval_id,
            "approver_id": approver_id,
            "status": status
        }
        if comment:
            data["comment"] = comment
        response = requests.post(url, json=data, headers=self._get_headers())
        return response.json()

    def update_finance_approval(self, approval_id: int, **kwargs) -> dict:
        """
        更新财务审批
        PUT /finance-approvals?approval_id={approval_id}
        @param approval_id: 审批ID
        @param kwargs: 更新字段
        @return: 响应字典
        """
        url = self._get_url("finance-approvals")
        response = requests.put(url, params={"approval_id": approval_id}, json=kwargs, headers=self._get_headers())
        return response.json()

    def delete_finance_approval(self, approval_id: int) -> dict:
        """
        删除财务审批
        DELETE /finance-approvals?approval_id={approval_id}
        @param approval_id: 审批ID
        @return: 响应字典
        """
        url = self._get_url("finance-approvals")
        response = requests.delete(url, params={"approval_id": approval_id}, headers=self._get_headers())
        return response.json()

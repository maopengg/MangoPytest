# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description:
# @Time   : 2024-03-17 19:50
# @Author : 毛鹏
from urllib.parse import urljoin

import requests


class ReimbursementAPI:
    """报销申请API - 对应 /reimbursements 接口"""

    def __init__(self):
        self._host = "http://localhost:8003"
        self._token = None

    def set_host(self, host: str):
        """设置API服务器地址"""
        self._host = host.rstrip("/")

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

    def get_reimbursements(self) -> dict:
        """
        获取报销申请列表
        GET /reimbursements
        @return: 响应字典
        """
        url = self._get_url("reimbursements")
        response = requests.get(url, headers=self._get_headers())
        return response.json()

    def get_reimbursement_by_id(self, reimbursement_id: int) -> dict:
        """
        根据ID获取报销申请
        GET /reimbursements?id={reimbursement_id}
        @param reimbursement_id: 报销申请ID
        @return: 响应字典
        """
        url = self._get_url("reimbursements")
        response = requests.get(url, params={"id": reimbursement_id}, headers=self._get_headers())
        return response.json()

    def create_reimbursement(self, user_id: int, amount: float, reason: str) -> dict:
        """
        创建报销申请
        POST /reimbursements
        @param user_id: 用户ID
        @param amount: 报销金额
        @param reason: 报销原因
        @return: 响应字典
        """
        url = self._get_url("reimbursements")
        response = requests.post(
            url,
            json={"user_id": user_id, "amount": amount, "reason": reason},
            headers=self._get_headers()
        )
        return response.json()

    def update_reimbursement(self, reimbursement_id: int, **kwargs) -> dict:
        """
        更新报销申请
        PUT /reimbursements/{reimbursement_id}
        @param reimbursement_id: 报销申请ID
        @param kwargs: 更新字段
        @return: 响应字典
        """
        url = self._get_url(f"reimbursements/{reimbursement_id}")
        response = requests.put(url, json=kwargs, headers=self._get_headers())
        return response.json()

    def delete_reimbursement(self, reimbursement_id: int) -> dict:
        """
        删除报销申请
        DELETE /reimbursements/{reimbursement_id}
        @param reimbursement_id: 报销申请ID
        @return: 响应字典
        """
        url = self._get_url(f"reimbursements/{reimbursement_id}")
        response = requests.delete(url, headers=self._get_headers())
        return response.json()

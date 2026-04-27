# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 报销申请API - 不依赖Excel装饰器
# @Time   : 2026-04-25
# @Author : 毛鹏

from typing import Dict, Any, List, Optional

from core.api.client import APIClient


class ReimbursementAPI:
    """报销申请API类 - 直接调用API，不依赖Excel"""

    def __init__(self, base_url: str = "http://43.142.161.61:8003", headers: Dict = None):
        self.client = APIClient(base_url=base_url)
        if headers:
            self.client.headers = headers

    def create_reimbursement(self, user_id: int, amount: float, reason: str,
                             category: str = "travel",
                             attachments: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        创建报销申请接口
        @param user_id: 用户ID
        @param amount: 报销金额
        @param reason: 报销原因
        @param category: 报销类别 (travel, office, entertainment, other)
        @param attachments: 附件列表
        @return: 响应数据字典
        """
        data = {
            "user_id": user_id,
            "amount": amount,
            "reason": reason,
            "category": category
        }
        if attachments:
            data["attachments"] = attachments

        response = self.client.post("/reimbursements", json=data)
        return response.data

    def get_all_reimbursements(self, status: Optional[str] = None) -> Dict[str, Any]:
        """
        获取所有报销申请接口
        @param status: 状态筛选 (pending, dept_approved, finance_approved, ceo_approved, rejected)
        @return: 响应数据字典
        """
        params = {}
        if status:
            params["status"] = status

        response = self.client.get("/reimbursements", params=params if params else None)
        return response.data

    def get_reimbursement_by_id(self, reimbursement_id: int) -> Dict[str, Any]:
        """
        根据ID获取报销申请接口
        @param reimbursement_id: 报销申请ID
        @return: 响应数据字典
        """
        response = self.client.get(f"/reimbursements/{reimbursement_id}")
        return response.data

    def update_reimbursement(self, reimbursement_id: int, amount: Optional[float] = None,
                             reason: Optional[str] = None,
                             category: Optional[str] = None) -> Dict[str, Any]:
        """
        更新报销申请接口
        @param reimbursement_id: 报销申请ID
        @param amount: 报销金额
        @param reason: 报销原因
        @param category: 报销类别
        @return: 响应数据字典
        """
        data = {}
        if amount is not None:
            data["amount"] = amount
        if reason is not None:
            data["reason"] = reason
        if category is not None:
            data["category"] = category

        response = self.client.put(f"/reimbursements/{reimbursement_id}", json=data)
        return response.data

    def delete_reimbursement(self, reimbursement_id: int) -> Dict[str, Any]:
        """
        删除报销申请接口
        @param reimbursement_id: 报销申请ID
        @return: 响应数据字典
        """
        response = self.client.delete(f"/reimbursements/{reimbursement_id}")
        return response.data

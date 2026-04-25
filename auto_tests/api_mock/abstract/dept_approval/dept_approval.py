# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 部门审批API - 不依赖Excel装饰器
# @Time   : 2026-04-25
# @Author : 毛鹏

from typing import Dict, Any, Optional

from core.api.client import APIClient


class DeptApprovalAPI:
    """部门审批API类 - 直接调用API，不依赖Excel"""

    def __init__(self, base_url: str = "http://43.142.161.61:8003", headers: Dict = None):
        self.client = APIClient(base_url=base_url)
        if headers:
            self.client.headers = headers

    def create_dept_approval(self, reimbursement_id: int, approver_id: int,
                             status: str = "approved",
                             comment: Optional[str] = None) -> Dict[str, Any]:
        """
        创建部门审批接口
        @param reimbursement_id: 报销申请ID
        @param approver_id: 审批人ID
        @param status: 审批状态 (approved, rejected)
        @param comment: 审批意见
        @return: 响应数据字典
        """
        data = {
            "reimbursement_id": reimbursement_id,
            "approver_id": approver_id,
            "status": status
        }
        if comment:
            data["comment"] = comment

        response = self.client.post("/dept-approvals", json=data)
        return response.data

    def get_all_dept_approvals(self, reimbursement_id: Optional[int] = None) -> Dict[str, Any]:
        """
        获取所有部门审批接口
        @param reimbursement_id: 按报销申请ID筛选
        @return: 响应数据字典
        """
        params = {}
        if reimbursement_id:
            params["reimbursement_id"] = reimbursement_id

        response = self.client.get("/dept-approvals", params=params if params else None)
        return response.data

    def get_dept_approval_by_id(self, approval_id: int) -> Dict[str, Any]:
        """
        根据ID获取部门审批接口
        @param approval_id: 审批ID
        @return: 响应数据字典
        """
        response = self.client.get(f"/dept-approvals/{approval_id}")
        return response.data

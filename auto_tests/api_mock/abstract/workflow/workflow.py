# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 审批工作流API - 不依赖Excel装饰器
# @Time   : 2026-04-25
# @Author : 毛鹏

from typing import Dict, Any

from core.api.client import APIClient


class WorkflowAPI:
    """审批工作流API类 - 直接调用API，不依赖Excel"""

    def __init__(self, base_url: str = "http://43.142.161.61:8003", headers: Dict = None):
        self.client = APIClient(base_url=base_url)
        if headers:
            self.client.headers = headers

    def get_workflow(self, reimbursement_id: int) -> Dict[str, Any]:
        """
        获取完整审批流程接口
        @param reimbursement_id: 报销申请ID
        @return: 响应数据字典
        """
        response = self.client.get(f"/workflow/{reimbursement_id}")
        return response.data

    def get_workflow_status(self, reimbursement_id: int) -> str:
        """
        获取报销申请的当前状态
        @param reimbursement_id: 报销申请ID
        @return: 状态字符串
        """
        response = self.get_workflow(reimbursement_id)
        if response.get("code") == 200:
            return response.get("data", {}).get("reimbursement", {}).get("status", "")
        return ""

    def is_fully_approved(self, reimbursement_id: int) -> bool:
        """
        检查报销申请是否已完全审批通过
        @param reimbursement_id: 报销申请ID
        @return: 是否完全通过
        """
        status = self.get_workflow_status(reimbursement_id)
        return status == "fully_approved"

    def is_rejected(self, reimbursement_id: int) -> bool:
        """
        检查报销申请是否已被拒绝
        @param reimbursement_id: 报销申请ID
        @return: 是否被拒绝
        """
        status = self.get_workflow_status(reimbursement_id)
        return status == "rejected"

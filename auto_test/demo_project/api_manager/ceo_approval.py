# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 总经理审批API - A级模块
# @Time   : 2026-03-31
# @Author : 毛鹏
from urllib.parse import urljoin

from models.api_model import ApiDataModel
from tools.base_request.request_tool import RequestTool


class CEOApprovalAPI(RequestTool):
    """总经理审批API - 对应 /ceo-approvals 接口 (A级模块，依赖B级)"""

    def __init__(self):
        super().__init__()
        self._host = "http://localhost:8003"

    def set_host(self, host: str):
        """设置API服务器地址"""
        self._host = host.rstrip('/')

    def _get_url(self, path: str) -> str:
        """获取完整URL"""
        return urljoin(self._host + "/", path)

    def create_ceo_approval(self, data: ApiDataModel) -> ApiDataModel:
        """
        创建总经理审批
        POST /ceo-approvals
        @param data: ApiDataModel (包含 reimbursement_id, finance_approval_id, approver_id, status, comment)
        @return: ApiDataModel
        """
        data.request.url = self._get_url("ceo-approvals")
        return self.http(data)

    def get_ceo_approvals(self, data: ApiDataModel) -> ApiDataModel:
        """
        获取总经理审批列表
        GET /ceo-approvals
        @param data: ApiDataModel
        @return: ApiDataModel
        """
        data.request.url = self._get_url("ceo-approvals")
        return self.http(data)

    def get_workflow(self, data: ApiDataModel) -> ApiDataModel:
        """
        获取完整审批流程
        GET /workflow/{reimbursement_id}
        @param data: ApiDataModel
        @return: ApiDataModel
        """
        reimbursement_id = data.request.params.get('reimbursement_id')
        data.request.url = self._get_url(f"workflow/{reimbursement_id}")
        return self.http(data)

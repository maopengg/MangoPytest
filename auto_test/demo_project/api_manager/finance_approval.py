# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 财务审批API - B级模块
# @Time   : 2026-03-31
# @Author : 毛鹏
from urllib.parse import urljoin

from models.api_model import ApiDataModel
from tools.base_request.request_tool import RequestTool


class FinanceApprovalAPI(RequestTool):
    """财务审批API - 对应 /finance-approvals 接口 (B级模块，依赖C级)"""

    def __init__(self):
        super().__init__()
        self._host = "http://localhost:8003"

    def set_host(self, host: str):
        """设置API服务器地址"""
        self._host = host.rstrip('/')

    def _get_url(self, path: str) -> str:
        """获取完整URL"""
        return urljoin(self._host + "/", path)

    def create_finance_approval(self, data: ApiDataModel) -> ApiDataModel:
        """
        创建财务审批
        POST /finance-approvals
        @param data: ApiDataModel (包含 reimbursement_id, dept_approval_id, approver_id, status, comment)
        @return: ApiDataModel
        """
        data.request.url = self._get_url("finance-approvals")
        return self.http(data)

    def get_finance_approvals(self, data: ApiDataModel) -> ApiDataModel:
        """
        获取财务审批列表
        GET /finance-approvals
        @param data: ApiDataModel
        @return: ApiDataModel
        """
        data.request.url = self._get_url("finance-approvals")
        return self.http(data)

    def update_finance_approval(self, data: ApiDataModel) -> ApiDataModel:
        """
        更新财务审批
        PUT /finance-approvals/{approval_id}
        @param data: ApiDataModel
        @return: ApiDataModel
        """
        approval_id = data.request.params.get('approval_id')
        data.request.url = self._get_url(f"finance-approvals/{approval_id}")
        return self.http(data)

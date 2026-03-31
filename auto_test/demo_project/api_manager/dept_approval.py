# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 部门审批API - C级模块
# @Time   : 2026-03-31
# @Author : 毛鹏
from urllib.parse import urljoin

from models.api_model import ApiDataModel
from tools.base_request.request_tool import RequestTool


class DeptApprovalAPI(RequestTool):
    """部门审批API - 对应 /dept-approvals 接口 (C级模块，依赖D级)"""

    def __init__(self):
        super().__init__()
        self._host = "http://localhost:8003"

    def set_host(self, host: str):
        """设置API服务器地址"""
        self._host = host.rstrip('/')

    def _get_url(self, path: str) -> str:
        """获取完整URL"""
        return urljoin(self._host + "/", path)

    def create_dept_approval(self, data: ApiDataModel) -> ApiDataModel:
        """
        创建部门审批
        POST /dept-approvals
        @param data: ApiDataModel (包含 reimbursement_id, approver_id, status, comment)
        @return: ApiDataModel
        """
        data.request.url = self._get_url("dept-approvals")
        return self.http(data)

    def get_dept_approvals(self, data: ApiDataModel) -> ApiDataModel:
        """
        获取部门审批列表
        GET /dept-approvals
        @param data: ApiDataModel
        @return: ApiDataModel
        """
        data.request.url = self._get_url("dept-approvals")
        return self.http(data)

    def update_dept_approval(self, data: ApiDataModel) -> ApiDataModel:
        """
        更新部门审批
        PUT /dept-approvals/{approval_id}
        @param data: ApiDataModel
        @return: ApiDataModel
        """
        approval_id = data.request.params.get('approval_id')
        data.request.url = self._get_url(f"dept-approvals/{approval_id}")
        return self.http(data)

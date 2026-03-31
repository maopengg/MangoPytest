# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 报销申请API - D级模块
# @Time   : 2026-03-31
# @Author : 毛鹏
from urllib.parse import urljoin

from models.api_model import ApiDataModel
from tools.base_request.request_tool import RequestTool


class ReimbursementAPI(RequestTool):
    """报销申请API - 对应 /reimbursements 接口 (D级模块)"""

    def __init__(self):
        super().__init__()
        self._host = "http://localhost:8003"

    def set_host(self, host: str):
        """设置API服务器地址"""
        self._host = host.rstrip('/')

    def _get_url(self, path: str) -> str:
        """获取完整URL"""
        return urljoin(self._host + "/", path)

    def create_reimbursement(self, data: ApiDataModel) -> ApiDataModel:
        """
        创建报销申请
        POST /reimbursements
        @param data: ApiDataModel (包含 user_id, amount, reason)
        @return: ApiDataModel
        """
        data.request.url = self._get_url("reimbursements")
        return self.http(data)

    def get_reimbursements(self, data: ApiDataModel) -> ApiDataModel:
        """
        获取报销申请列表
        GET /reimbursements
        @param data: ApiDataModel
        @return: ApiDataModel
        """
        data.request.url = self._get_url("reimbursements")
        return self.http(data)

    def get_reimbursement_by_id(self, data: ApiDataModel) -> ApiDataModel:
        """
        根据ID获取报销申请
        GET /reimbursements?id={id}
        @param data: ApiDataModel
        @return: ApiDataModel
        """
        data.request.url = self._get_url("reimbursements")
        return self.http(data)

    def update_reimbursement(self, data: ApiDataModel) -> ApiDataModel:
        """
        更新报销申请
        PUT /reimbursements/{reimbursement_id}
        @param data: ApiDataModel
        @return: ApiDataModel
        """
        reimbursement_id = data.request.params.get('reimbursement_id')
        data.request.url = self._get_url(f"reimbursements/{reimbursement_id}")
        return self.http(data)

    def delete_reimbursement(self, data: ApiDataModel) -> ApiDataModel:
        """
        删除报销申请
        DELETE /reimbursements/{reimbursement_id}
        @param data: ApiDataModel
        @return: ApiDataModel
        """
        reimbursement_id = data.request.params.get('reimbursement_id')
        data.request.url = self._get_url(f"reimbursements/{reimbursement_id}")
        return self.http(data)

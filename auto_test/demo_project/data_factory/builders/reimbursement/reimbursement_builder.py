# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 报销申请构造器 - D级模块 (基础层)
# @Time   : 2026-03-31
# @Author : 毛鹏
from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime

from ..base_builder import BaseBuilder
from auto_test.demo_project.api_manager import demo_project
from ...registry import register_builder


@register_builder("reimbursement")
class ReimbursementBuilder(BaseBuilder):
    """
    报销申请构造器 - D级模块 (最基础层)
    对应 /reimbursements 接口
    不依赖其他模块，是审批流的起点
    """

    def __init__(self, token: str = None, factory=None):
        super().__init__(token, factory)

    def build(
        self, user_id: int = None, amount: float = None, reason: str = None
    ) -> Dict[str, Any]:
        """
        构造报销申请数据（不调用API）
        @param user_id: 用户ID
        @param amount: 报销金额
        @param reason: 报销原因
        @return: 报销申请数据字典
        """
        return {
            "user_id": user_id or 1,
            "amount": amount or 100.00,
            "reason": reason or f"差旅报销 - {uuid.uuid4().hex[:6]}",
        }

    def create(
        self, user_id: int = None, amount: float = None, reason: str = None
    ) -> Dict[str, Any]:
        """
        创建报销申请（调用API）
        @return: 创建的报销申请数据
        """
        reimbursement_data = self.build(user_id, amount, reason)

        api_data = self._create_api_data(
            url="/reimbursements", method="POST", json_data=reimbursement_data
        )

        result = demo_project.reimbursement.create_reimbursement(api_data)
        if result.response and result.response.json().get("code") == 200:
            created_reimbursement = result.response.json()["data"]
            self._register_created(created_reimbursement)
            return created_reimbursement
        return None

    def get_all(self) -> List[Dict[str, Any]]:
        """
        获取所有报销申请
        @return: 报销申请列表
        """
        api_data = self._create_api_data(url="/reimbursements", method="GET")

        result = demo_project.reimbursement.get_reimbursements(api_data)
        if result.response and result.response.json().get("code") == 200:
            return result.response.json()["data"]
        return []

    def get_by_id(self, reimbursement_id: int) -> Dict[str, Any]:
        """
        根据ID获取报销申请
        @param reimbursement_id: 报销申请ID
        @return: 报销申请数据
        """
        api_data = self._create_api_data(
            url="/reimbursements", method="GET", params={"id": reimbursement_id}
        )

        result = demo_project.reimbursement.get_reimbursement_by_id(api_data)
        if result.response and result.response.json().get("code") == 200:
            return result.response.json()["data"]
        return None

    def update(self, reimbursement_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新报销申请（仅在pending状态可更新）
        @param reimbursement_id: 报销申请ID
        @param data: 更新数据
        @return: 更新后的报销申请数据
        """
        api_data = self._create_api_data(
            url="/reimbursements",
            method="PUT",
            params={"reimbursement_id": reimbursement_id},
            json_data=data,
        )

        result = demo_project.reimbursement.update_reimbursement(api_data)
        if result.response and result.response.json().get("code") == 200:
            return result.response.json()["data"]
        return None

    def delete(self, reimbursement_id: int) -> bool:
        """
        删除报销申请
        @param reimbursement_id: 报销申请ID
        @return: 是否删除成功
        """
        api_data = self._create_api_data(
            url="/reimbursements",
            method="DELETE",
            params={"reimbursement_id": reimbursement_id},
        )

        result = demo_project.reimbursement.delete_reimbursement(api_data)
        if result.response and result.response.json().get("code") == 200:
            return True
        return False

    def is_pending(self, reimbursement_id: int) -> bool:
        """
        检查报销申请是否为pending状态
        @param reimbursement_id: 报销申请ID
        @return: 是否为pending状态
        """
        reimbursement = self.get_by_id(reimbursement_id)
        if reimbursement:
            return reimbursement.get("status") == "pending"
        return False

    def get_status(self, reimbursement_id: int) -> Optional[str]:
        """
        获取报销申请状态
        @param reimbursement_id: 报销申请ID
        @return: 状态字符串
        """
        reimbursement = self.get_by_id(reimbursement_id)
        if reimbursement:
            return reimbursement.get("status")
        return None

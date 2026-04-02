# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 部门审批实体 - C级模块
# @Time   : 2026-03-31
# @Author : 毛鹏
from dataclasses import dataclass
from typing import Optional, Dict, Any, List

from .base_entity import BaseEntity


@dataclass
class DeptApprovalEntity(BaseEntity):
    """
    部门审批实体 - C级模块
    
    对应 mock_api 中的 DeptApproval 模型
    依赖D级：Reimbursement（报销申请）
    
    Attributes:
        reimbursement_id: 报销申请ID（D级依赖）
        approver_id: 审批人ID
        status: 审批状态（approved/rejected）
        comment: 审批意见
    """

    # 审批信息
    reimbursement_id: int = 0  # D级依赖
    approver_id: int = 0
    status: str = "approved"  # approved, rejected
    comment: Optional[str] = None

    def validate(self) -> bool:
        """
        验证部门审批数据有效性
        
        @return: 是否有效
        """
        if self.reimbursement_id <= 0:
            return False

        if self.approver_id <= 0:
            return False

        if self.status not in ["approved", "rejected"]:
            return False

        return True

    def get_dependencies(self) -> List[str]:
        """获取依赖的实体类型"""
        return ["reimbursement"]  # 依赖报销申请实体

    def to_api_payload(self) -> Dict[str, Any]:
        """
        转换为API请求体
        
        @return: API请求体字典
        """
        payload = {
            "reimbursement_id": self.reimbursement_id,
            "approver_id": self.approver_id,
            "status": self.status
        }

        if self.comment:
            payload["comment"] = self.comment

        return payload

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "DeptApprovalEntity":
        """
        从API响应创建实体
        
        @param data: API响应数据
        @return: DeptApprovalEntity实例
        """
        entity = cls(
            id=data.get("id"),
            reimbursement_id=data.get("reimbursement_id", 0),
            approver_id=data.get("approver_id", 0),
            status=data.get("status", "approved"),
            comment=data.get("comment"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )
        entity._is_new = False
        return entity

    def is_approved(self) -> bool:
        """检查是否已通过"""
        return self.status == "approved"

    def is_rejected(self) -> bool:
        """检查是否已拒绝"""
        return self.status == "rejected"

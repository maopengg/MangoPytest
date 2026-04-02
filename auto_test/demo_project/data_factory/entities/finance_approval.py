# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 财务审批实体 - B级模块
# @Time   : 2026-03-31
# @Author : 毛鹏
from dataclasses import dataclass
from typing import Optional, Dict, Any, List

from .base_entity import BaseEntity


@dataclass
class FinanceApprovalEntity(BaseEntity):
    """
    财务审批实体 - B级模块
    
    对应 mock_api 中的 FinanceApproval 模型
    依赖C级：DeptApproval（部门审批）
    
    Attributes:
        reimbursement_id: 报销申请ID（D级）
        dept_approval_id: 部门审批ID（C级依赖）
        approver_id: 审批人ID
        status: 审批状态（approved/rejected）
        comment: 审批意见
    """

    # 审批信息
    reimbursement_id: int = 0  # D级
    dept_approval_id: int = 0  # C级依赖
    approver_id: int = 0
    status: str = "approved"  # approved, rejected
    comment: Optional[str] = None

    def validate(self) -> bool:
        """
        验证财务审批数据有效性
        
        @return: 是否有效
        """
        if self.reimbursement_id <= 0:
            return False

        if self.dept_approval_id <= 0:
            return False

        if self.approver_id <= 0:
            return False

        if self.status not in ["approved", "rejected"]:
            return False

        return True

    def get_dependencies(self) -> List[str]:
        """获取依赖的实体类型"""
        return ["reimbursement", "dept_approval"]  # 依赖报销申请和部门审批

    def to_api_payload(self) -> Dict[str, Any]:
        """
        转换为API请求体
        
        @return: API请求体字典
        """
        payload = {
            "reimbursement_id": self.reimbursement_id,
            "dept_approval_id": self.dept_approval_id,
            "approver_id": self.approver_id,
            "status": self.status
        }

        if self.comment:
            payload["comment"] = self.comment

        return payload

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "FinanceApprovalEntity":
        """
        从API响应创建实体
        
        @param data: API响应数据
        @return: FinanceApprovalEntity实例
        """
        entity = cls(
            id=data.get("id"),
            reimbursement_id=data.get("reimbursement_id", 0),
            dept_approval_id=data.get("dept_approval_id", 0),
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

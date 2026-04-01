# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 报销申请实体 - D级模块
# @Time   : 2026-03-31
# @Author : 毛鹏
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List

from .base_entity import BaseEntity


@dataclass
class ReimbursementEntity(BaseEntity):
    """
    报销申请实体 - D级模块（基础层）
    
    对应 mock_api 中的 Reimbursement 模型
    不依赖其他模块，是审批流的起点
    
    Attributes:
        user_id: 申请人ID
        amount: 报销金额
        reason: 报销原因
        status: 审批状态
    """
    
    # 报销信息
    user_id: int = 0
    amount: float = 0.0
    reason: str = ""
    
    # 审批状态
    # pending, dept_approved, dept_rejected, finance_approved, finance_rejected, ceo_approved, ceo_rejected
    
    def validate(self) -> bool:
        """
        验证报销申请数据有效性
        
        @return: 是否有效
        """
        if self.user_id <= 0:
            return False
        
        if self.amount <= 0:
            return False
        
        if not self.reason or len(self.reason.strip()) == 0:
            return False
        
        return True
    
    def get_dependencies(self) -> List[str]:
        """获取依赖的实体类型"""
        return ["user"]  # 依赖用户实体
    
    def to_api_payload(self) -> Dict[str, Any]:
        """
        转换为API请求体
        
        @return: API请求体字典
        """
        return {
            "user_id": self.user_id,
            "amount": self.amount,
            "reason": self.reason
        }
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "ReimbursementEntity":
        """
        从API响应创建实体
        
        @param data: API响应数据
        @return: ReimbursementEntity实例
        """
        entity = cls(
            id=data.get("id"),
            user_id=data.get("user_id", 0),
            amount=data.get("amount", 0.0),
            reason=data.get("reason", ""),
            status=data.get("status", "pending"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )
        entity._is_new = False
        return entity
    
    def is_pending(self) -> bool:
        """检查是否为待审批状态"""
        return self.status == "pending"
    
    def is_dept_approved(self) -> bool:
        """检查是否已通过部门审批"""
        return self.status in ["dept_approved", "finance_approved", "finance_rejected", "ceo_approved", "ceo_rejected"]
    
    def is_finance_approved(self) -> bool:
        """检查是否已通过财务审批"""
        return self.status in ["finance_approved", "ceo_approved", "ceo_rejected"]
    
    def is_fully_approved(self) -> bool:
        """检查是否已完全审批通过"""
        return self.status == "ceo_approved"
    
    def is_rejected(self) -> bool:
        """检查是否已被拒绝"""
        return self.status in ["dept_rejected", "finance_rejected", "ceo_rejected"]

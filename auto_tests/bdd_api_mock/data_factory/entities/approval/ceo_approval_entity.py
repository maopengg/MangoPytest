# -*- coding: utf-8 -*-
"""
总经理审批实体 - A级审批
"""

from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import Column, Integer, String, Text, Enum, DateTime, Index
from sqlalchemy.orm import relationship

from auto_tests.bdd_api_mock.config import Base


class CEOApprovalEntity(Base):
    """总经理审批实体"""
    __tablename__ = "ceo_approvals"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="审批ID")
    approval_no = Column(String(50), nullable=False, unique=True, comment="审批单号")
    # 数据库层面弱关联（无外键约束），只在 ORM 层面建立关系
    reimbursement_id = Column(Integer, nullable=False, comment="报销申请ID")
    finance_approval_id = Column(Integer, nullable=False, comment="财务审批ID")
    approver_id = Column(Integer, nullable=False, comment="审批人ID")
    status = Column(
        Enum("approved", "rejected"),
        nullable=False,
        comment="审批结果",
    )
    comment = Column(Text, comment="审批意见")
    approved_at = Column(DateTime, default=None, comment="审批时间")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")

    # 关联关系 - ORM 层面关联，数据库无外键约束
    reimbursement = relationship("ReimbursementEntity", back_populates="ceo_approvals")
    finance_approval = relationship("FinanceApprovalEntity", back_populates="ceo_approvals")

    # 索引
    __table_args__ = (
        Index("idx_reimbursement_id", "reimbursement_id"),
        Index("idx_finance_approval_id", "finance_approval_id"),
        Index("idx_approver_id", "approver_id"),
        Index("idx_status", "status"),
    )

    def to_api_payload(self) -> Dict[str, Any]:
        """序列化为 API 请求参数"""
        return {
            "reimbursement_id": self.reimbursement_id,
            "finance_approval_id": self.finance_approval_id,
            "approver_id": self.approver_id,
            "status": self.status,
            "comment": self.comment,
        }

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "approval_no": self.approval_no,
            "reimbursement_id": self.reimbursement_id,
            "finance_approval_id": self.finance_approval_id,
            "approver_id": self.approver_id,
            "status": self.status,
            "comment": self.comment,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<CEOApprovalEntity(id={self.id}, approval_no={self.approval_no}, status={self.status})>"

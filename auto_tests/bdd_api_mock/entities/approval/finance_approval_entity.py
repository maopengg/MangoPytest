# -*- coding: utf-8 -*-
"""
财务审批实体 - B级审批
"""

from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum, Boolean, DateTime, Index
from sqlalchemy.orm import relationship

from auto_tests.bdd_api_mock.config import Base


class FinanceApprovalEntity(Base):
    """财务审批实体"""
    __tablename__ = "finance_approvals"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="审批ID")
    approval_no = Column(String(50), nullable=False, unique=True, comment="审批单号")
    reimbursement_id = Column(Integer, ForeignKey("reimbursements.id"), nullable=False, comment="报销申请ID")
    dept_approval_id = Column(Integer, ForeignKey("dept_approvals.id"), nullable=False, comment="部门审批ID")
    approver_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="审批人ID")
    status = Column(
        Enum("approved", "rejected"),
        nullable=False,
        comment="审批结果",
    )
    comment = Column(Text, comment="审批意见")
    finance_check_passed = Column(Boolean, default=False, comment="财务核查通过")
    approved_at = Column(DateTime, default=None, comment="审批时间")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")

    # 关联关系
    reimbursement = relationship("ReimbursementEntity", back_populates="finance_approvals")
    dept_approval = relationship("DeptApprovalEntity", back_populates="finance_approvals")
    ceo_approvals = relationship("CEOApprovalEntity", back_populates="finance_approval")

    # 索引
    __table_args__ = (
        Index("idx_reimbursement_id", "reimbursement_id"),
        Index("idx_dept_approval_id", "dept_approval_id"),
        Index("idx_approver_id", "approver_id"),
        Index("idx_status", "status"),
    )

    def to_api_payload(self) -> Dict[str, Any]:
        """序列化为 API 请求参数"""
        return {
            "reimbursement_id": self.reimbursement_id,
            "dept_approval_id": self.dept_approval_id,
            "approver_id": self.approver_id,
            "status": self.status,
            "comment": self.comment,
            "finance_check_passed": self.finance_check_passed,
        }

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "approval_no": self.approval_no,
            "reimbursement_id": self.reimbursement_id,
            "dept_approval_id": self.dept_approval_id,
            "approver_id": self.approver_id,
            "status": self.status,
            "comment": self.comment,
            "finance_check_passed": self.finance_check_passed,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<FinanceApprovalEntity(id={self.id}, approval_no={self.approval_no}, status={self.status})>"

# -*- coding: utf-8 -*-
"""
报销申请实体
"""

from datetime import datetime
from typing import Any, Dict, Optional, List
from decimal import Decimal

from sqlalchemy import Column, Integer, String, Numeric, Text, Enum, DateTime, Index
from sqlalchemy.orm import relationship

from auto_tests.bdd_api_mock.config import Base


class ReimbursementEntity(Base):
    """报销申请实体"""
    __tablename__ = "reimbursements"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="报销ID")
    reimb_no = Column(String(50), nullable=False, unique=True, comment="报销单号")
    # 数据库层面弱关联（无外键约束），只在 ORM 层面建立关系
    user_id = Column(Integer, nullable=False, comment="申请人ID")
    amount = Column(Numeric(12, 2), nullable=False, comment="报销金额")
    reason = Column(Text, nullable=False, comment="报销原因")
    category = Column(String(50), default="general", comment="报销类别")
    attachments = Column(Text, comment="附件列表(JSON)")
    status = Column(
        Enum(
            "pending",
            "dept_approved",
            "dept_rejected",
            "finance_approved",
            "finance_rejected",
            "ceo_approved",
            "ceo_rejected",
            "paid",
        ),
        default="pending",
        comment="审批状态",
    )
    current_step = Column(Integer, default=1, comment="当前步骤(1-D级,2-C级,3-B级,4-A级)")
    submitted_at = Column(DateTime, default=datetime.now, comment="提交时间")
    completed_at = Column(DateTime, default=None, comment="完成时间")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        comment="更新时间",
    )

    # 关联关系 - ORM 级联删除：删除报销时自动删除关联的审批和日志
    # 注意：数据库层面保持弱关联（无外键约束），级联只在 ORM 层面生效
    user = relationship("UserEntity", back_populates="reimbursements")
    dept_approvals = relationship(
        "DeptApprovalEntity",
        back_populates="reimbursement",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    finance_approvals = relationship(
        "FinanceApprovalEntity",
        back_populates="reimbursement",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    ceo_approvals = relationship(
        "CEOApprovalEntity",
        back_populates="reimbursement",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    approval_logs = relationship(
        "ApprovalLogEntity",
        back_populates="reimbursement",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    # 索引
    __table_args__ = (
        Index("idx_reimb_no", "reimb_no"),
        Index("idx_user_id", "user_id"),
        Index("idx_status", "status"),
        Index("idx_created_at", "created_at"),
    )

    def to_api_payload(self) -> Dict[str, Any]:
        """序列化为 API 请求参数"""
        return {
            "user_id": self.user_id,
            "amount": float(self.amount) if isinstance(self.amount, Decimal) else self.amount,
            "reason": self.reason,
            "category": self.category,
        }

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "reimb_no": self.reimb_no,
            "user_id": self.user_id,
            "amount": float(self.amount) if isinstance(self.amount, Decimal) else self.amount,
            "reason": self.reason,
            "category": self.category,
            "attachments": self.attachments,
            "status": self.status,
            "current_step": self.current_step,
            "submitted_at": self.submitted_at.isoformat() if self.submitted_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f"<ReimbursementEntity(id={self.id}, reimb_no={self.reimb_no}, status={self.status})>"

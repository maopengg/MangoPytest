# -*- coding: utf-8 -*-
"""
审批流程日志实体
"""

from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import Column, Integer, String, Text, DateTime, Index
from sqlalchemy.orm import relationship

from auto_tests.bdd_api_mock.config import Base


class ApprovalLogEntity(Base):
    """审批流程日志实体"""
    __tablename__ = "approval_logs"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="日志ID")
    # 数据库层面弱关联（无外键约束），只在 ORM 层面建立关系
    reimbursement_id = Column(Integer, nullable=False, comment="报销申请ID")
    step = Column(Integer, nullable=False, comment="审批步骤(1-4)")
    step_name = Column(String(50), nullable=False, comment="步骤名称")
    action = Column(String(50), nullable=False, comment="操作类型")
    operator_id = Column(Integer, nullable=False, comment="操作人ID")
    operator_name = Column(String(100), comment="操作人姓名")
    comment = Column(Text, comment="操作备注")
    old_status = Column(String(50), comment="原状态")
    new_status = Column(String(50), comment="新状态")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")

    # 关联关系 - ORM 层面关联，数据库无外键约束
    reimbursement = relationship("ReimbursementEntity", back_populates="approval_logs")

    # 索引
    __table_args__ = (
        Index("idx_reimbursement_id", "reimbursement_id"),
        Index("idx_created_at", "created_at"),
    )

    def to_api_payload(self) -> Dict[str, Any]:
        """序列化为 API 请求参数"""
        return {
            "reimbursement_id": self.reimbursement_id,
            "step": self.step,
            "step_name": self.step_name,
            "action": self.action,
            "operator_id": self.operator_id,
            "comment": self.comment,
        }

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "reimbursement_id": self.reimbursement_id,
            "step": self.step,
            "step_name": self.step_name,
            "action": self.action,
            "operator_id": self.operator_id,
            "operator_name": self.operator_name,
            "comment": self.comment,
            "old_status": self.old_status,
            "new_status": self.new_status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<ApprovalLogEntity(id={self.id}, step={self.step}, action={self.action})>"

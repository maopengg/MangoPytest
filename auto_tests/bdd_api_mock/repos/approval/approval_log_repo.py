# -*- coding: utf-8 -*-
"""
审批日志 Repository
"""

from typing import List
from sqlalchemy import select
from sqlalchemy.orm import Session

from core.base import BaseRepository
from auto_tests.bdd_api_mock.data_factory.entities.approval.approval_log_entity import ApprovalLogEntity


class ApprovalLogRepo(BaseRepository[ApprovalLogEntity]):
    """审批日志 Repository"""
    model = ApprovalLogEntity
    CODE_FIELD = None  # 日志不需要按模式清理

    def __init__(self, session: Session):
        super().__init__(session)

    def get_by_reimbursement(self, reimbursement_id: int, limit: int = 100) -> List[ApprovalLogEntity]:
        """根据报销ID获取日志"""
        stmt = select(ApprovalLogEntity).where(
            ApprovalLogEntity.reimbursement_id == reimbursement_id
        ).order_by(ApprovalLogEntity.created_at).limit(limit)
        return list(self.session.execute(stmt).scalars().all())

    def get_by_operator(self, operator_id: int, limit: int = 100) -> List[ApprovalLogEntity]:
        """根据操作人获取日志"""
        stmt = select(ApprovalLogEntity).where(
            ApprovalLogEntity.operator_id == operator_id
        ).limit(limit)
        return list(self.session.execute(stmt).scalars().all())

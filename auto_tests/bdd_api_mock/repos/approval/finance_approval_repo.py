# -*- coding: utf-8 -*-
"""
财务审批 Repository
"""

from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.orm import Session

from auto_tests.bdd_api_mock.repos.base import BaseRepository
from auto_tests.bdd_api_mock.entities.approval.finance_approval_entity import FinanceApprovalEntity


class FinanceApprovalRepo(BaseRepository[FinanceApprovalEntity]):
    """财务审批 Repository"""
    model = FinanceApprovalEntity
    CODE_FIELD = "approval_no"

    def __init__(self, session: Session):
        super().__init__(session)

    def get_by_approval_no(self, approval_no: str) -> Optional[FinanceApprovalEntity]:
        """根据审批单号获取"""
        stmt = select(FinanceApprovalEntity).where(FinanceApprovalEntity.approval_no == approval_no)
        return self.session.execute(stmt).scalar_one_or_none()

    def get_by_reimbursement(self, reimbursement_id: int) -> Optional[FinanceApprovalEntity]:
        """根据报销ID获取"""
        stmt = select(FinanceApprovalEntity).where(
            FinanceApprovalEntity.reimbursement_id == reimbursement_id
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def get_by_approver(self, approver_id: int, limit: int = 100) -> List[FinanceApprovalEntity]:
        """根据审批人获取"""
        stmt = select(FinanceApprovalEntity).where(
            FinanceApprovalEntity.approver_id == approver_id
        ).limit(limit)
        return list(self.session.execute(stmt).scalars().all())

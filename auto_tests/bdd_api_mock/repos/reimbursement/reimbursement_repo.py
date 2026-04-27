# -*- coding: utf-8 -*-
"""
报销申请 Repository
"""

from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.orm import Session

from auto_tests.bdd_api_mock.repos.base import BaseRepository
from auto_tests.bdd_api_mock.data_factory.entities.reimbursement.reimbursement_entity import ReimbursementEntity


class ReimbursementRepo(BaseRepository[ReimbursementEntity]):
    """报销申请 Repository"""
    model = ReimbursementEntity
    CODE_FIELD = "reimb_no"

    def __init__(self, session: Session):
        super().__init__(session)

    def get_by_reimb_no(self, reimb_no: str) -> Optional[ReimbursementEntity]:
        """根据报销单号获取"""
        stmt = select(ReimbursementEntity).where(ReimbursementEntity.reimb_no == reimb_no)
        return self.session.execute(stmt).scalar_one_or_none()

    def get_by_user_id(self, user_id: int, limit: int = 100) -> List[ReimbursementEntity]:
        """根据用户ID获取"""
        stmt = select(ReimbursementEntity).where(
            ReimbursementEntity.user_id == user_id
        ).limit(limit)
        return list(self.session.execute(stmt).scalars().all())

    def get_by_status(self, status: str, limit: int = 100) -> List[ReimbursementEntity]:
        """根据状态获取"""
        stmt = select(ReimbursementEntity).where(
            ReimbursementEntity.status == status
        ).limit(limit)
        return list(self.session.execute(stmt).scalars().all())

    def get_pending(self, limit: int = 100) -> List[ReimbursementEntity]:
        """获取待审批的报销"""
        stmt = select(ReimbursementEntity).where(
            ReimbursementEntity.status == "pending"
        ).limit(limit)
        return list(self.session.execute(stmt).scalars().all())

# -*- coding: utf-8 -*-
"""
数据提交 Repository
"""

from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.orm import Session

from auto_tests.bdd_api_mock.repos.base import BaseRepository
from auto_tests.bdd_api_mock.entities.data.data_entity import DataSubmissionEntity


class DataSubmissionRepo(BaseRepository[DataSubmissionEntity]):
    """数据提交 Repository"""
    model = DataSubmissionEntity
    CODE_FIELD = "name"

    def __init__(self, session: Session):
        super().__init__(session)

    def get_by_name(self, name: str) -> Optional[DataSubmissionEntity]:
        """根据名称获取数据"""
        stmt = select(DataSubmissionEntity).where(DataSubmissionEntity.name == name)
        return self.session.execute(stmt).scalar_one_or_none()

    def get_by_submitter(self, submitter_id: int, limit: int = 100) -> List[DataSubmissionEntity]:
        """根据提交者获取数据"""
        stmt = select(DataSubmissionEntity).where(
            DataSubmissionEntity.submitter_id == submitter_id
        ).limit(limit)
        return list(self.session.execute(stmt).scalars().all())

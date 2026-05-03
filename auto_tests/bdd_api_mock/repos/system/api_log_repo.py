# -*- coding: utf-8 -*-
"""
API日志 Repository
"""

from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.orm import Session

from core.base import BaseRepository
from auto_tests.bdd_api_mock.data_factory.entities.system.api_log_entity import APILogEntity


class APILogRepo(BaseRepository[APILogEntity]):
    """API日志 Repository"""
    model = APILogEntity
    CODE_FIELD = None  # 日志不需要按模式清理

    def __init__(self, session: Session):
        super().__init__(session)

    def get_by_request_id(self, request_id: str) -> Optional[APILogEntity]:
        """根据请求ID获取日志"""
        stmt = select(APILogEntity).where(APILogEntity.request_id == request_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def get_by_path(self, path: str, limit: int = 100) -> List[APILogEntity]:
        """根据路径获取日志"""
        stmt = select(APILogEntity).where(
            APILogEntity.path == path
        ).limit(limit)
        return list(self.session.execute(stmt).scalars().all())

    def get_by_user(self, user_id: int, limit: int = 100) -> List[APILogEntity]:
        """根据用户获取日志"""
        stmt = select(APILogEntity).where(
            APILogEntity.user_id == user_id
        ).limit(limit)
        return list(self.session.execute(stmt).scalars().all())

# -*- coding: utf-8 -*-
"""
系统健康状态 Repository
"""

from typing import Optional, List
from sqlalchemy import select

from auto_tests.bdd_api_mock.repos.base import BaseRepository
from auto_tests.bdd_api_mock.entities.system import HealthEntity


class HealthRepo(BaseRepository[HealthEntity]):
    """系统健康状态 Repository"""
    model = HealthEntity
    CODE_FIELD = "status"

    def get_current_health(self) -> Optional[HealthEntity]:
        """获取当前健康状态（最新一条）"""
        stmt = select(HealthEntity).order_by(HealthEntity.updated_at.desc()).limit(1)
        return self.session.execute(stmt).scalar_one_or_none()

    def get_by_status(self, status: str) -> List[HealthEntity]:
        """根据状态获取健康记录"""
        stmt = select(HealthEntity).where(HealthEntity.status == status)
        return list(self.session.execute(stmt).scalars().all())

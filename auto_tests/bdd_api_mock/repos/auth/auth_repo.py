# -*- coding: utf-8 -*-
"""
认证 Repository
"""

from typing import Optional, List
from sqlalchemy import select

from auto_tests.bdd_api_mock.repos.base import BaseRepository
from auto_tests.bdd_api_mock.data_factory.entities.auth import AuthEntity


class AuthRepo(BaseRepository[AuthEntity]):
    """认证 Repository"""
    model = AuthEntity
    CODE_FIELD = "username"

    def get_by_username(self, username: str) -> Optional[AuthEntity]:
        """根据用户名获取会话"""
        stmt = select(AuthEntity).where(AuthEntity.username == username)
        return self.session.execute(stmt).scalar_one_or_none()

    def get_by_token(self, token: str) -> Optional[AuthEntity]:
        """根据令牌获取会话"""
        stmt = select(AuthEntity).where(AuthEntity.token == token)
        return self.session.execute(stmt).scalar_one_or_none()

    def get_active_sessions(self) -> List[AuthEntity]:
        """获取所有活跃会话"""
        from datetime import datetime
        stmt = select(AuthEntity).where(AuthEntity.expires_at > datetime.now())
        return list(self.session.execute(stmt).scalars().all())

# -*- coding: utf-8 -*-
"""
用户 Repository
"""

from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.orm import Session

from core.base import BaseRepository
from auto_tests.bdd_api_mock.data_factory.entities.user.user_entity import UserEntity


class UserRepo(BaseRepository[UserEntity]):
    """用户 Repository"""
    model = UserEntity
    CODE_FIELD = "username"

    def __init__(self, session: Session):
        super().__init__(session)

    def get_by_username(self, username: str) -> Optional[UserEntity]:
        """根据用户名获取用户"""
        stmt = select(UserEntity).where(
            UserEntity.username == username,
            UserEntity.status == "active"
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def get_by_role(self, role: str, limit: int = 100) -> List[UserEntity]:
        """根据角色获取用户列表"""
        stmt = select(UserEntity).where(
            UserEntity.role == role,
            UserEntity.status == "active"
        ).limit(limit)
        return list(self.session.execute(stmt).scalars().all())

    def get_active_users(self, limit: int = 100) -> List[UserEntity]:
        """获取所有活跃用户"""
        stmt = select(UserEntity).where(
            UserEntity.status == "active"
        ).limit(limit)
        return list(self.session.execute(stmt).scalars().all())

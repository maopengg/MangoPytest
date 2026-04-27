# -*- coding: utf-8 -*-
"""
认证实体
用于存储登录会话信息
"""

from typing import Any, Dict
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func

from auto_tests.bdd_api_mock.config import Base


class AuthEntity(Base):
    """认证实体 - 登录会话"""
    __tablename__ = "auth_sessions"
    __table_args__ = {"comment": "登录会话表"}

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    user_id = Column(Integer, nullable=False, comment="用户ID")
    username = Column(String(50), nullable=False, comment="用户名")
    token = Column(String(255), nullable=False, comment="认证令牌")
    role = Column(String(50), nullable=True, comment="用户角色")
    expires_at = Column(DateTime, nullable=True, comment="过期时间")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")

    def to_api_payload(self) -> Dict[str, Any]:
        """序列化为 API 请求参数"""
        return {
            "username": self.username,
            "password": "",  # 登录时传入
        }

    def __repr__(self):
        return f"<AuthEntity(id={self.id}, username={self.username}, role={self.role})>"

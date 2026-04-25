# -*- coding: utf-8 -*-
"""
用户实体
"""

from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import Column, Integer, String, Enum, DateTime, Index
from sqlalchemy.orm import relationship

from auto_tests.bdd_api_mock.config import Base


class UserEntity(Base):
    """用户实体"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="用户ID")
    username = Column(String(50), nullable=False, unique=True, comment="用户名")
    email = Column(String(100), nullable=False, comment="邮箱")
    full_name = Column(String(100), nullable=False, comment="全名")
    password = Column(String(255), nullable=False, comment="密码(MD5加密)")
    role = Column(
        Enum("user", "admin", "manager", "finance", "ceo"),
        default="user",
        comment="角色",
    )
    status = Column(
        Enum("active", "inactive", "deleted"),
        default="active",
        comment="状态",
    )
    last_login_at = Column(DateTime, default=None, comment="最后登录时间")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        comment="更新时间",
    )

    # 关联关系 - ORM 级联删除：删除用户时自动删除关联的订单和报销
    # 注意：数据库层面保持弱关联（无外键约束），级联只在 ORM 层面生效
    orders = relationship(
        "OrderEntity",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    reimbursements = relationship(
        "ReimbursementEntity",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    # 索引
    __table_args__ = (
        Index("idx_username", "username"),
        Index("idx_role", "role"),
        Index("idx_status", "status"),
    )

    def to_api_payload(self) -> Dict[str, Any]:
        """序列化为 API 请求参数"""
        return {
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "password": self.password,
            "role": self.role,
        }

    def to_dict(self, exclude_password: bool = True) -> Dict[str, Any]:
        """转换为字典"""
        result = {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "role": self.role,
            "status": self.status,
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        if not exclude_password:
            result["password"] = self.password
        return result

    def __repr__(self):
        return f"<UserEntity(id={self.id}, username={self.username}, role={self.role})>"

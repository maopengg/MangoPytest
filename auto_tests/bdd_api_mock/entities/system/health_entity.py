# -*- coding: utf-8 -*-
"""
系统健康状态实体
"""

from typing import Any, Dict
from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.sql import func

from auto_tests.bdd_api_mock.config import Base


class HealthEntity(Base):
    """系统健康状态实体"""
    __tablename__ = "system_health"
    __table_args__ = {"comment": "系统健康状态表"}

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    status = Column(String(50), nullable=False, default="healthy", comment="健康状态")
    version = Column(String(50), nullable=True, comment="系统版本")
    uptime = Column(Integer, nullable=True, comment="运行时间(秒)")
    checks = Column(JSON, nullable=True, comment="健康检查详情")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    def to_api_payload(self) -> Dict[str, Any]:
        """序列化为 API 响应格式"""
        return {
            "status": self.status,
            "version": self.version,
            "uptime": self.uptime,
            "checks": self.checks or {},
        }

    def __repr__(self):
        return f"<HealthEntity(id={self.id}, status={self.status})>"

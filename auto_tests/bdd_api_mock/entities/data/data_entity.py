# -*- coding: utf-8 -*-
"""
数据提交实体
"""

from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import Column, Integer, String, DateTime, Index

from auto_tests.bdd_api_mock.config import Base


class DataSubmissionEntity(Base):
    """数据提交实体"""
    __tablename__ = "data_submissions"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="提交ID")
    name = Column(String(100), nullable=False, comment="数据名称")
    value = Column(Integer, nullable=False, comment="数据值")
    submitter_id = Column(Integer, default=None, comment="提交者ID")
    source_ip = Column(String(50), default=None, comment="来源IP")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")

    # 索引
    __table_args__ = (
        Index("idx_name", "name"),
        Index("idx_created_at", "created_at"),
    )

    def to_api_payload(self) -> Dict[str, Any]:
        """序列化为 API 请求参数"""
        return {
            "name": self.name,
            "value": self.value,
        }

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "value": self.value,
            "submitter_id": self.submitter_id,
            "source_ip": self.source_ip,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<DataSubmissionEntity(id={self.id}, name={self.name}, value={self.value})>"

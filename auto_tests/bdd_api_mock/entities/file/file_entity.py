# -*- coding: utf-8 -*-
"""
文件实体
"""

from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import Column, Integer, String, DateTime, Index

from auto_tests.bdd_api_mock.config import Base


class FileEntity(Base):
    """文件实体"""
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="文件ID")
    file_id = Column(String(50), nullable=False, unique=True, comment="文件唯一标识")
    filename = Column(String(255), nullable=False, comment="文件名")
    original_name = Column(String(255), nullable=False, comment="原始文件名")
    content_type = Column(String(100), default=None, comment="文件类型")
    size = Column(Integer, default=0, comment="文件大小(字节)")
    file_path = Column(String(500), default=None, comment="文件存储路径")
    uploader_id = Column(Integer, default=None, comment="上传者ID")
    download_count = Column(Integer, default=0, comment="下载次数")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")

    # 索引
    __table_args__ = (
        Index("idx_file_id", "file_id"),
        Index("idx_uploader", "uploader_id"),
        Index("idx_created_at", "created_at"),
    )

    def to_api_payload(self) -> Dict[str, Any]:
        """序列化为 API 请求参数"""
        return {
            "filename": self.original_name,
            "content_type": self.content_type,
        }

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "file_id": self.file_id,
            "filename": self.filename,
            "original_name": self.original_name,
            "content_type": self.content_type,
            "size": self.size,
            "file_path": self.file_path,
            "uploader_id": self.uploader_id,
            "download_count": self.download_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<FileEntity(id={self.id}, file_id={self.file_id}, filename={self.filename})>"

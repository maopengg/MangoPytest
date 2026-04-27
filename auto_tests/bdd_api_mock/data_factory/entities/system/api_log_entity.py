# -*- coding: utf-8 -*-
"""
API调用日志实体
"""

from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import Column, Integer, String, Text, DateTime, Index

from auto_tests.bdd_api_mock.config import Base


class APILogEntity(Base):
    """API调用日志实体"""
    __tablename__ = "api_logs"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="日志ID")
    request_id = Column(String(50), nullable=False, comment="请求ID")
    method = Column(String(10), nullable=False, comment="请求方法")
    path = Column(String(255), nullable=False, comment="请求路径")
    query_params = Column(Text, comment="查询参数")
    request_body = Column(Text, comment="请求体")
    response_body = Column(Text, comment="响应体")
    status_code = Column(Integer, comment="响应状态码")
    user_id = Column(Integer, default=None, comment="用户ID")
    client_ip = Column(String(50), comment="客户端IP")
    user_agent = Column(String(500), comment="用户代理")
    duration_ms = Column(Integer, comment="执行时长(毫秒)")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")

    # 索引
    __table_args__ = (
        Index("idx_request_id", "request_id"),
        Index("idx_path", "path"),
        Index("idx_user_id", "user_id"),
        Index("idx_created_at", "created_at"),
    )

    def to_api_payload(self) -> Dict[str, Any]:
        """序列化为 API 请求参数"""
        return {
            "request_id": self.request_id,
            "method": self.method,
            "path": self.path,
            "status_code": self.status_code,
        }

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "request_id": self.request_id,
            "method": self.method,
            "path": self.path,
            "query_params": self.query_params,
            "request_body": self.request_body,
            "response_body": self.response_body,
            "status_code": self.status_code,
            "user_id": self.user_id,
            "client_ip": self.client_ip,
            "user_agent": self.user_agent,
            "duration_ms": self.duration_ms,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<APILogEntity(id={self.id}, method={self.method}, path={self.path})>"

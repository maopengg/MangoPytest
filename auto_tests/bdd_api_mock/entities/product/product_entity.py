# -*- coding: utf-8 -*-
"""
产品实体
"""

from datetime import datetime
from typing import Any, Dict, Optional
from decimal import Decimal

from sqlalchemy import Column, Integer, String, Numeric, Text, Enum, DateTime, Index
from sqlalchemy.orm import relationship

from auto_tests.bdd_api_mock.config import Base


class ProductEntity(Base):
    """产品实体"""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="产品ID")
    name = Column(String(200), nullable=False, comment="产品名称")
    price = Column(Numeric(10, 2), nullable=False, comment="价格")
    description = Column(Text, comment="产品描述")
    stock = Column(Integer, default=0, comment="库存数量")
    category = Column(String(50), default="general", comment="产品分类")
    status = Column(
        Enum("active", "inactive", "deleted"),
        default="active",
        comment="状态",
    )
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        comment="更新时间",
    )

    # 关联关系 - ORM 级联删除：删除产品时自动删除关联的订单
    # 注意：数据库层面保持弱关联（无外键约束），级联只在 ORM 层面生效
    orders = relationship(
        "OrderEntity",
        back_populates="product",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    # 索引
    __table_args__ = (
        Index("idx_name", "name"),
        Index("idx_category", "category"),
        Index("idx_status", "status"),
    )

    def to_api_payload(self) -> Dict[str, Any]:
        """序列化为 API 请求参数"""
        return {
            "name": self.name,
            "price": float(self.price) if isinstance(self.price, Decimal) else self.price,
            "description": self.description,
            "stock": self.stock,
        }

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "price": float(self.price) if isinstance(self.price, Decimal) else self.price,
            "description": self.description,
            "stock": self.stock,
            "category": self.category,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f"<ProductEntity(id={self.id}, name={self.name}, price={self.price})>"

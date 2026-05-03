# -*- coding: utf-8 -*-
"""
订单实体
"""

from datetime import datetime
from typing import Any, Dict, Optional
from decimal import Decimal

from sqlalchemy import Column, Integer, String, Numeric, Text, ForeignKey, Enum, DateTime, Index
from sqlalchemy.orm import relationship

from auto_tests.bdd_api_mock.config import Base


class OrderEntity(Base):
    """订单实体"""
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="订单ID")
    order_no = Column(String(50), nullable=False, unique=True, comment="订单编号")
    # 数据库层面弱关联（无外键约束），只在 ORM 层面建立关系
    product_id = Column(Integer, nullable=False, comment="产品ID")
    user_id = Column(Integer, nullable=False, comment="用户ID")
    quantity = Column(Integer, nullable=False, comment="数量")
    unit_price = Column(Numeric(10, 2), nullable=False, comment="单价")
    total_amount = Column(Numeric(10, 2), nullable=False, comment="总金额")
    status = Column(
        Enum("pending", "paid", "shipped", "completed", "cancelled"),
        default="pending",
        comment="订单状态",
    )
    remark = Column(Text, comment="备注")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        comment="更新时间",
    )

    # 关联关系 - ORM 层面关联，数据库无外键约束
    product = relationship("ProductEntity", back_populates="orders", primaryjoin="foreign(OrderEntity.product_id) == ProductEntity.id")
    user = relationship("UserEntity", back_populates="orders", primaryjoin="foreign(OrderEntity.user_id) == UserEntity.id")

    # 索引
    __table_args__ = (
        Index("idx_order_no", "order_no"),
        Index("idx_user_id", "user_id"),
        Index("idx_status", "status"),
        Index("idx_created_at", "created_at"),
    )

    def to_api_payload(self) -> Dict[str, Any]:
        """序列化为 API 请求参数"""
        return {
            "product_id": self.product_id,
            "user_id": self.user_id,
            "quantity": self.quantity,
        }

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "order_no": self.order_no,
            "product_id": self.product_id,
            "user_id": self.user_id,
            "quantity": self.quantity,
            "unit_price": float(self.unit_price) if isinstance(self.unit_price, Decimal) else self.unit_price,
            "total_amount": float(self.total_amount) if isinstance(self.total_amount, Decimal) else self.total_amount,
            "status": self.status,
            "remark": self.remark,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f"<OrderEntity(id={self.id}, order_no={self.order_no}, status={self.status})>"

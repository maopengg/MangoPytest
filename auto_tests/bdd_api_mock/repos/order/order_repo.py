# -*- coding: utf-8 -*-
"""
订单 Repository
"""

from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.orm import Session

from auto_tests.bdd_api_mock.repos.base import BaseRepository
from auto_tests.bdd_api_mock.data_factory.entities.order.order_entity import OrderEntity


class OrderRepo(BaseRepository[OrderEntity]):
    """订单 Repository"""
    model = OrderEntity
    CODE_FIELD = "order_no"

    def __init__(self, session: Session):
        super().__init__(session)

    def get_by_order_no(self, order_no: str) -> Optional[OrderEntity]:
        """根据订单号获取订单"""
        stmt = select(OrderEntity).where(OrderEntity.order_no == order_no)
        return self.session.execute(stmt).scalar_one_or_none()

    def get_by_user_id(self, user_id: int, limit: int = 100) -> List[OrderEntity]:
        """根据用户ID获取订单"""
        stmt = select(OrderEntity).where(
            OrderEntity.user_id == user_id
        ).limit(limit)
        return list(self.session.execute(stmt).scalars().all())

    def get_by_status(self, status: str, limit: int = 100) -> List[OrderEntity]:
        """根据状态获取订单"""
        stmt = select(OrderEntity).where(
            OrderEntity.status == status
        ).limit(limit)
        return list(self.session.execute(stmt).scalars().all())

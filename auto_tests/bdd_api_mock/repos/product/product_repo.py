# -*- coding: utf-8 -*-
"""
产品 Repository
"""

from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.orm import Session

from auto_tests.bdd_api_mock.repos.base import BaseRepository
from auto_tests.bdd_api_mock.entities.product.product_entity import ProductEntity


class ProductRepo(BaseRepository[ProductEntity]):
    """产品 Repository"""
    model = ProductEntity
    CODE_FIELD = "name"

    def __init__(self, session: Session):
        super().__init__(session)

    def get_by_name(self, name: str) -> Optional[ProductEntity]:
        """根据名称获取产品"""
        stmt = select(ProductEntity).where(ProductEntity.name == name)
        return self.session.execute(stmt).scalar_one_or_none()

    def get_by_category(self, category: str, limit: int = 100) -> List[ProductEntity]:
        """根据分类获取产品"""
        stmt = select(ProductEntity).where(
            ProductEntity.category == category,
            ProductEntity.status == "active"
        ).limit(limit)
        return list(self.session.execute(stmt).scalars().all())

    def get_active_products(self, limit: int = 100) -> List[ProductEntity]:
        """获取所有活跃产品"""
        stmt = select(ProductEntity).where(
            ProductEntity.status == "active"
        ).limit(limit)
        return list(self.session.execute(stmt).scalars().all())

# -*- coding: utf-8 -*-
"""
Repository 基类

UI 测试与 API 测试共用同一套数据管理逻辑：
通过 session.delete() 触发 ORM cascade，自动级联清理。
"""
from typing import TypeVar, Generic, Type, Optional, List, Any, Dict
from sqlalchemy.orm import Session
from sqlalchemy import select, update

T = TypeVar("T")


class BaseRepository(Generic[T]):
    model: Type[T] = None
    CODE_FIELD: str = None

    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, id: int) -> Optional[T]:
        return self.session.get(self.model, id)

    def get_all(self, limit: int = 100) -> List[T]:
        stmt = select(self.model).limit(limit)
        return list(self.session.execute(stmt).scalars().all())

    def create(self, entity: T) -> T:
        self.session.add(entity)
        self.session.commit()
        self.session.refresh(entity)
        return entity

    def update(self, id: int, data: Dict[str, Any]) -> Optional[T]:
        stmt = update(self.model).where(self.model.id == id).values(**data)
        self.session.execute(stmt)
        self.session.commit()
        return self.get_by_id(id)

    def delete(self, id: int) -> bool:
        entity = self.get_by_id(id)
        if entity:
            self.session.delete(entity)
            self.session.commit()
            return True
        return False

    def delete_by_pattern(self, pattern: str = "AUTO_%") -> int:
        if not self.CODE_FIELD:
            return 0
        stmt = select(self.model).where(
            getattr(self.model, self.CODE_FIELD).like(pattern)
        )
        entities = list(self.session.execute(stmt).scalars().all())
        for entity in entities:
            self.session.delete(entity)
        self.session.commit()
        return len(entities)

    def delete_auto_test_data(self) -> int:
        return self.delete_by_pattern("AUTO_%")

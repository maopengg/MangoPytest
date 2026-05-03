# -*- coding: utf-8 -*-
"""
Repository 基类

提供通用 CRUD 和数据清理的 Repository 基类。
通过 session.delete() 触发 ORM cascade，自动级联删除子表。
"""

from typing import TypeVar, Generic, Type, Optional, List, Any, Dict
from sqlalchemy.orm import Session
from sqlalchemy import select, update

T = TypeVar("T")


class BaseRepository(Generic[T]):
    """Repository 基类"""

    model: Type[T] = None
    CODE_FIELD: str = None  # 用于模式匹配清理的字段名

    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, id: int) -> Optional[T]:
        """根据ID获取实体"""
        return self.session.get(self.model, id)

    def get_all(self, limit: int = 100) -> List[T]:
        """获取所有实体"""
        stmt = select(self.model).limit(limit)
        return list(self.session.execute(stmt).scalars().all())

    def create(self, entity: T) -> T:
        """创建实体"""
        self.session.add(entity)
        self.session.commit()
        self.session.refresh(entity)
        return entity

    def update(self, id: int, data: Dict[str, Any]) -> Optional[T]:
        """更新实体"""
        stmt = update(self.model).where(self.model.id == id).values(**data)
        self.session.execute(stmt)
        self.session.commit()
        return self.get_by_id(id)

    def delete(self, id: int) -> bool:
        """删除实体"""
        entity = self.get_by_id(id)
        if entity:
            self.session.delete(entity)
            self.session.commit()
            return True
        return False

    def delete_by_pattern(self, pattern: str = "AUTO_%") -> int:
        """
        按模式删除数据（ORM 级联删除）

        通过 session.delete() 触发 relationship 上配置的 cascade，
        自动级联删除关联的子表记录，不依赖清理顺序。
        """
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
        """
        删除 AUTO_ 开头的自动化测试数据

        ORM 级联删除：只需要删顶层实体，关联的子表记录由
        relationship 上的 cascade 自动处理。
        """
        return self.delete_by_pattern("AUTO_%")

    def count(self) -> int:
        """获取总数"""
        from sqlalchemy import func

        stmt = select(func.count()).select_from(self.model)
        return self.session.execute(stmt).scalar()

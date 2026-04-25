# -*- coding: utf-8 -*-
"""
Repository 基类
"""

from typing import TypeVar, Generic, Type, Optional, List, Any, Dict
from sqlalchemy.orm import Session
from sqlalchemy import select, delete, update

from auto_tests.bdd_api_mock.config import Base

T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    """Repository 基类"""

    model: Type[T] = None
    CODE_FIELD: str = None  # 用于模式匹配清理的字段名
    
    # 外键关联配置（用于没有 CODE_FIELD 的表）
    # 格式: [(外键字段名, 关联表名, 关联表CODE_FIELD)]
    FK_CLEANUP_CONFIG: List[tuple] = []

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
        """按模式删除数据（用于清理测试数据）"""
        if not self.CODE_FIELD:
            return 0
        stmt = delete(self.model).where(
            getattr(self.model, self.CODE_FIELD).like(pattern)
        )
        result = self.session.execute(stmt)
        self.session.commit()
        return result.rowcount

    def delete_by_foreign_key(
        self, 
        fk_field: str, 
        related_table: str, 
        related_code_field: str,
        pattern: str = "AUTO_%"
    ) -> int:
        """
        通过外键关联删除数据
        
        适用于没有 CODE_FIELD 的表，通过外键关联到有 CODE_FIELD 的表进行删除
        
        Args:
            fk_field: 外键字段名（如 user_id, product_id）
            related_table: 关联表名（如 users, products）
            related_code_field: 关联表的 CODE_FIELD（如 username, name）
            pattern: 匹配模式，默认 "AUTO_%"
            
        Returns:
            删除的记录数
        """
        # 构建子查询：找出关联表中匹配模式的 ID
        subquery = select(
            getattr(self.model, fk_field)
        ).where(
            getattr(self.model, fk_field).in_(
                select(
                    getattr(Base.metadata.tables[related_table].c, 'id')
                ).where(
                    getattr(Base.metadata.tables[related_table].c, related_code_field).like(pattern)
                )
            )
        )
        
        # 删除匹配的记录
        stmt = delete(self.model).where(
            getattr(self.model, fk_field).in_(subquery)
        )
        result = self.session.execute(stmt)
        self.session.commit()
        return result.rowcount

    def delete_auto_test_data(self) -> int:
        """
        删除 AUTO_ 开头的自动化测试数据
        
        策略：
        1. 如果有 CODE_FIELD，直接按模式删除
        2. 如果有 FK_CLEANUP_CONFIG，通过外键关联删除
        3. 否则返回 0
        """
        total = 0
        
        # 1. 如果有 CODE_FIELD，直接删除
        if self.CODE_FIELD:
            total += self.delete_by_pattern("AUTO_%")
        
        # 2. 如果有外键关联配置，通过外键删除
        if hasattr(self, 'FK_CLEANUP_CONFIG') and self.FK_CLEANUP_CONFIG:
            for fk_config in self.FK_CLEANUP_CONFIG:
                if len(fk_config) >= 3:
                    fk_field, related_table, related_code_field = fk_config[:3]
                    count = self.delete_by_foreign_key(
                        fk_field, 
                        related_table, 
                        related_code_field,
                        "AUTO_%"
                    )
                    total += count
        
        return total

    def count(self) -> int:
        """获取总数"""
        from sqlalchemy import func

        stmt = select(func.count()).select_from(self.model)
        return self.session.execute(stmt).scalar()

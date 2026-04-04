# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 组织构造器 - C层依赖基石（D级）
# @Time   : 2026-04-02
# @Author : 毛鹏

import uuid
from typing import Optional

from core.base import BaseBuilder, BuilderContext
from core.enums import DependencyLevel
from ...entities.org_entity import OrgEntity
from ...registry import register_builder


@register_builder("org")
class OrgBuilder(BaseBuilder[OrgEntity]):
    """组织构造器"""

    DEPENDENCY_LEVEL = DependencyLevel.LEVEL_D
    DEPENDENCIES = []

    def __init__(
            self,
            token: str = None,
            context: BuilderContext = None,
            strategy=None,
            parent_builders=None,
            factory=None,
    ):
        super().__init__(
            token=token,
            context=context,
            strategy=strategy,
            parent_builders=parent_builders,
            factory=factory,
        )

    def build(
            self,
            name: str = None,
            code: str = None,
            budget_total: float = 1000000,
            level: int = 1,
            parent_id: str = None,
    ) -> OrgEntity:
        uid = uuid.uuid4().hex[:6]
        return OrgEntity(
            name=name or f"组织_{uid}",
            code=code or f"ORG{uid.upper()}",
            budget_total=budget_total,
            level=level,
            parent_id=parent_id,
            status="active",
        )

    def create(
            self,
            entity: OrgEntity = None,
            auto_prepare_deps: bool = True,
            **kwargs,
    ) -> Optional[OrgEntity]:
        if entity is None:
            entity = self.build(**kwargs)

        created = self._do_create(entity)
        if created:
            return created

        # 当前项目无组织API时，允许本地构造实体继续测试链路
        self._register_created(entity)
        return entity

    def get_by_id(self, org_id: str) -> Optional[OrgEntity]:
        result = self.context.strategy.get_by_id(OrgEntity, org_id)
        return result.entity if result.success else None

    def update(self, entity: OrgEntity, **kwargs) -> Optional[OrgEntity]:
        for key, value in kwargs.items():
            if hasattr(entity, key):
                setattr(entity, key, value)

        result = self.context.strategy.update(entity, **kwargs)
        return result.entity if result.success else entity

    def delete(self, entity: OrgEntity = None, org_id: str = None) -> bool:
        delete_id = org_id if org_id is not None else (entity.id if entity else None)
        if not delete_id:
            return False
        result = self.context.strategy.delete(OrgEntity, delete_id)
        if result.success and entity:
            entity.mark_as_deleted()
        return result.success

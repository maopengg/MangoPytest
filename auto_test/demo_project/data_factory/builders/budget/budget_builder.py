# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 预算构造器 - 依赖组织（C级）
# @Time   : 2026-04-02
# @Author : 毛鹏

from typing import Optional, Dict, Any

from ..base_builder import BaseBuilder, BuilderContext, DependencyLevel
from ...entities.budget_entity import BudgetEntity
from ...registry import register_builder


@register_builder("budget")
class BudgetBuilder(BaseBuilder[BudgetEntity]):
    """预算构造器"""

    DEPENDENCY_LEVEL = DependencyLevel.LEVEL_C
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
        self._org_builder = None

    def _get_org_builder(self):
        if self._org_builder is None:
            from ..org.org_builder import OrgBuilder

            self._org_builder = self._get_or_create_builder(OrgBuilder)
        return self._org_builder

    def _prepare_dependencies(self, **kwargs) -> Dict[str, Any]:
        if kwargs.get("org_id"):
            return kwargs

        if self.context.auto_prepare_deps:
            org_builder = self._get_org_builder()
            org = org_builder.create()
            if org:
                kwargs["org_id"] = org.id
        return kwargs

    def build(
        self,
        org_id: str = None,
        total_amount: float = 500000,
        category: str = "project",
        year: int = 2026,
        status: str = "active",
    ) -> BudgetEntity:
        return BudgetEntity(
            org_id=org_id,
            total_amount=total_amount,
            category=category,
            year=year,
            status=status,
        )

    def create(
        self,
        entity: BudgetEntity = None,
        auto_prepare_deps: bool = True,
        **kwargs,
    ) -> Optional[BudgetEntity]:
        if auto_prepare_deps:
            kwargs = self._prepare_dependencies(**kwargs)

        if entity is None:
            entity = self.build(**kwargs)

        created = self._do_create(entity)
        if created:
            return created

        # 当前项目无预算API时，允许本地构造实体继续测试链路
        self._register_created(entity)
        return entity

    def get_by_id(self, budget_id: str) -> Optional[BudgetEntity]:
        result = self.context.strategy.get_by_id(BudgetEntity, budget_id)
        return result.entity if result.success else None

    def update(self, entity: BudgetEntity, **kwargs) -> Optional[BudgetEntity]:
        for key, value in kwargs.items():
            if hasattr(entity, key):
                setattr(entity, key, value)

        result = self.context.strategy.update(entity, **kwargs)
        return result.entity if result.success else entity

    def delete(self, entity: BudgetEntity = None, budget_id: str = None) -> bool:
        delete_id = budget_id if budget_id is not None else (entity.id if entity else None)
        if not delete_id:
            return False
        result = self.context.strategy.delete(BudgetEntity, delete_id)
        if result.success and entity:
            entity.mark_as_deleted()
        return result.success

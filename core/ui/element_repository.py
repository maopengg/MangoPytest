"""UI 元素源到 mangoautomation 运行时模型的公共仓库。"""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from core.sources.ui_elements import load_ui_element_records
from core.ui.element_runtime import ElementDefinition


class SourceElementRepository:
    """按数据源、产品以及可选页面范围查询唯一元素。"""

    def __init__(
        self,
        *,
        source: str,
        project: str,
        product_name: str,
        module_name: str | None = None,
        page_name: str | None = None,
    ) -> None:
        self.source = source
        self.project = project
        self.product_name = product_name
        self.module_name = module_name
        self.page_name = page_name

    @lru_cache(maxsize=1)
    def all(self) -> tuple[ElementDefinition, ...]:
        return tuple(
            ElementDefinition.from_record(record)
            for record in load_ui_element_records(
                source=self.source,
                project=self.project,
                product_name=self.product_name,
            )
            if self._matches_scope(record)
        )

    @lru_cache(maxsize=512)
    def get(
        self,
        name: str,
        module_name: str | None = None,
        page_name: str | None = None,
    ) -> ElementDefinition:
        matched = [
            definition
            for definition in self.all()
            if definition.name == name
            and (module_name is None or definition.module_name == module_name)
            and (page_name is None or definition.page_name == page_name)
        ]
        if not matched:
            raise KeyError(f"UI 元素仓库中不存在：{name}")
        if len(matched) > 1:
            raise ValueError(
                f"UI 元素仓库中存在 {len(matched)} 个同名元素，"
                f"请指定模块或页面：{name}"
            )
        return matched[0]

    def _matches_scope(self, record: dict[str, Any]) -> bool:
        return (
            (self.module_name is None or record.get("模块名称") == self.module_name)
            and (self.page_name is None or record.get("页面名称") == self.page_name)
        )


@lru_cache(maxsize=32)
def source_element_repository(
    *,
    source: str,
    project: str,
    product_name: str,
    module_name: str | None = None,
    page_name: str | None = None,
) -> SourceElementRepository:
    """返回同一元素配置对应的共享仓库。"""
    return SourceElementRepository(
        source=source,
        project=project,
        product_name=product_name,
        module_name=module_name,
        page_name=page_name,
    )


def configured_element_repository(
    settings,
    *,
    module_name: str | None = None,
    page_name: str | None = None,
) -> SourceElementRepository:
    """根据项目设置创建或复用公共元素仓库。"""
    return source_element_repository(
        source=str(settings.ELEMENT_SOURCE),
        project=str(settings.ELEMENT_PROJECT),
        product_name=str(settings.ELEMENT_PRODUCT),
        module_name=module_name,
        page_name=page_name,
    )

"""pytest UI Demo 自己维护的本地 Excel 元素仓库。"""

from dataclasses import dataclass
from functools import lru_cache
from typing import Any

from playwright.sync_api import Locator, Page

from .excel_loader import load_element_records


@dataclass(frozen=True)
class ElementDefinition:
    element_id: int
    project_name: str
    module_name: str
    page_name: str
    name: str
    locating_method: str | int
    expression: str
    index: int | None = None
    tag: str | None = None
    input_type: str | None = None
    role: str | None = None
    description: str | None = None
    interactive: bool = False
    disabled: bool = False

    @classmethod
    def from_record(cls, record: dict[str, Any]) -> "ElementDefinition":
        return cls(
            element_id=int(record["ID"]),
            project_name=str(record["项目名称"]),
            module_name=str(record["模块名称"]),
            page_name=str(record["页面名称"]),
            name=str(record["元素名称"]),
            locating_method=record["定位方式1"],
            expression=str(record["表达式1"]),
            index=_optional_int(record.get("下标1")),
            tag=_optional_text(record.get("标签")),
            input_type=_optional_text(record.get("input类型")),
            role=_optional_text(record.get("role")),
            description=_optional_text(record.get("说明")),
            interactive=_bool(record.get("可交互")),
            disabled=_bool(record.get("禁用")),
        )

    def locate(self, page: Page) -> Locator:
        method = str(self.locating_method).strip().upper()
        if method in {"TEST_ID", "1"}:
            locator = page.get_by_test_id(self.expression)
        elif method in {"CSS", "9"}:
            locator = page.locator(self.expression)
        elif method in {"TEXT", "3"}:
            locator = page.get_by_text(self.expression, exact=True)
        elif method in {"PLACEHOLDER", "4"}:
            locator = page.get_by_placeholder(self.expression)
        elif method in {"XPATH", "0"}:
            value = self.expression
            locator = page.locator(value if value.startswith("xpath=") else f"xpath={value}")
        else:
            raise ValueError(f"不支持的定位方式: {self.locating_method}")
        return locator.nth(self.index) if self.index is not None else locator


class ElementRepository:
    @staticmethod
    @lru_cache(maxsize=1)
    def all_local() -> tuple[ElementDefinition, ...]:
        return tuple(
            ElementDefinition.from_record(record) for record in load_element_records()
        )

    @lru_cache(maxsize=512)
    def get(self, name: str) -> ElementDefinition:
        matched = [item for item in self.all_local() if item.name == name]
        if len(matched) != 1:
            raise KeyError(f"pytest_ui 元素不唯一或不存在: {name}")
        return matched[0]

    def locate(self, page: Page, name: str) -> Locator:
        return self.get(name).locate(page)


elements = ElementRepository()


def _optional_int(value: Any) -> int | None:
    return None if value in (None, "") else int(value)


def _optional_text(value: Any) -> str | None:
    return None if value in (None, "") else str(value)


def _bool(value: Any) -> bool:
    return str(value).strip().lower() in {"是", "true", "1", "yes"}

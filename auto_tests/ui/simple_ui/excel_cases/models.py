"""UI Mock Excel 用例模型。"""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class OperationCase:
    """一条 mangoautomation 方法覆盖用例。"""

    case_id: str
    group: str
    method: str
    description: str
    target_id: str
    params: dict[str, Any]
    expected: str
    verify_id: str
    priority: str


@dataclass(frozen=True)
class ElementCase:
    """一条页面交互控件用例。"""

    case_id: str
    page_key: str
    element_id: str
    control_type: str
    method: str
    params: dict[str, Any]
    expected: str
    risk: str


@dataclass(frozen=True)
class InventoryCase:
    """一条全元素定位验证用例。"""

    sequence: int
    page_key: str
    element_id: str
    tag: str
    interactive: bool
    disabled: bool
    strategy: str

    @property
    def case_id(self) -> str:
        return f"UI-ID-{self.sequence:03d}"

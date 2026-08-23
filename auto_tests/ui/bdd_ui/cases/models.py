from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class OperationCase:
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
    sequence: int
    page_key: str
    element_id: str
    tag: str
    interactive: bool
    disabled: bool
    strategy: str

    @property
    def case_id(self) -> str:
        return f"BDD-UI-ID-{self.sequence:03d}"

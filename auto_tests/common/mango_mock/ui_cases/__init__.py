"""Mango Mock UI 能力用例模型与加载器。"""

from .loader import load_ui_capability_cases
from .classification import (
    ELEMENT_CATEGORY_LABELS,
    INVENTORY_PAGE_LABELS,
    OPERATION_CATEGORY_LABELS,
    group_element_cases,
    group_inventory_cases,
    group_operation_cases,
)
from .metadata import (
    MANGO_MOCK_UI_EPIC,
    PAGE_LABELS,
    apply_element_case_metadata,
    apply_inventory_case_metadata,
    apply_operation_case_metadata,
)
from .models import ElementCase, InventoryCase, OperationCase

__all__ = [
    "ElementCase",
    "ELEMENT_CATEGORY_LABELS",
    "InventoryCase",
    "INVENTORY_PAGE_LABELS",
    "MANGO_MOCK_UI_EPIC",
    "OperationCase",
    "OPERATION_CATEGORY_LABELS",
    "PAGE_LABELS",
    "apply_element_case_metadata",
    "apply_inventory_case_metadata",
    "apply_operation_case_metadata",
    "group_element_cases",
    "group_inventory_cases",
    "group_operation_cases",
    "load_ui_capability_cases",
]

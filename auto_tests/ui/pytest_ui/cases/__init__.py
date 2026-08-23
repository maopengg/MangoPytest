"""pytest_ui 原生参数化用例。"""

from .loader import ELEMENT_CASES, INVENTORY_CASES, OPERATION_CASES
from .models import ElementCase, InventoryCase, OperationCase

__all__ = [
    "ELEMENT_CASES", "ElementCase", "INVENTORY_CASES", "InventoryCase",
    "OPERATION_CASES", "OperationCase",
]

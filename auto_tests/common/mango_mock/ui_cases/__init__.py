"""Mango Mock UI 能力用例模型与加载器。"""

from .loader import load_ui_capability_cases
from .models import ElementCase, InventoryCase, OperationCase

__all__ = [
    "ElementCase",
    "InventoryCase",
    "OperationCase",
    "load_ui_capability_cases",
]

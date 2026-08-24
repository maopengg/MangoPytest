"""以 pytest Case ID 装配公共 Mango Mock UI 能力用例。"""

from pathlib import Path

from auto_tests.common.mango_mock.ui_cases import (
    ElementCase,
    InventoryCase,
    OperationCase,
    load_ui_capability_cases,
)
from auto_tests.ui.pytest_ui.config import settings

OPERATION_CASES, ELEMENT_CASES, INVENTORY_CASES = load_ui_capability_cases(
    case_file=Path(__file__).resolve().parents[2] / "data" / "cases.json",
    settings=settings,
    project_label="pytest_ui",
    inventory_prefix="PYTEST-UI-ID",
)

__all__ = [
    "ELEMENT_CASES", "ElementCase", "INVENTORY_CASES", "InventoryCase",
    "OPERATION_CASES", "OperationCase",
]

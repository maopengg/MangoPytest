"""Mango Mock UI 能力 Case 的统一报告分类。"""

from __future__ import annotations

from core.execution import apply_case_metadata

from .classification import (
    ELEMENT_CATEGORY_LABELS,
    INVENTORY_PAGE_LABELS,
    OPERATION_CATEGORY_LABELS,
)
from .models import ElementCase, InventoryCase, OperationCase


MANGO_MOCK_UI_EPIC = "Mango Mock UI 自动化"
PAGE_LABELS = {
    "global": "全局导航",
    "componentsPage": "组件实验室",
    "httpPage": "HTTP 业务",
    "scenariosPage": "场景编排",
    "ssePage": "SSE 事件流",
    "websocketPage": "WebSocket 双向通信",
    "mcpPage": "MCP 协议",
    "grpcPage": "gRPC 协议",
}


def apply_operation_case_metadata(case: OperationCase, category: str | None = None) -> None:
    apply_case_metadata(
        case_id=case.case_id,
        title=f"{case.method} {case.description}",
        epic=MANGO_MOCK_UI_EPIC,
        feature=OPERATION_CATEGORY_LABELS.get(category, "mangoautomation 操作能力"),
        story=None if category else case.group,
    )


def apply_element_case_metadata(case: ElementCase, category: str | None = None) -> None:
    apply_case_metadata(
        case_id=case.case_id,
        title=f"操作 {case.element_id}（{case.control_type}）",
        epic=MANGO_MOCK_UI_EPIC,
        feature=ELEMENT_CATEGORY_LABELS.get(category, "UI 控件交互"),
        story=PAGE_LABELS.get(case.page_key, case.page_key),
    )


def apply_inventory_case_metadata(case: InventoryCase, category: str | None = None) -> None:
    apply_case_metadata(
        case_id=case.case_id,
        title=f"定位 {case.element_id}",
        epic=MANGO_MOCK_UI_EPIC,
        feature=INVENTORY_PAGE_LABELS.get(category, "UI 元素定位"),
        story=None if category else PAGE_LABELS.get(case.page_key, case.page_key),
    )


__all__ = [
    "MANGO_MOCK_UI_EPIC",
    "PAGE_LABELS",
    "apply_element_case_metadata",
    "apply_inventory_case_metadata",
    "apply_operation_case_metadata",
]

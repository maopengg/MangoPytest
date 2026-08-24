"""Mango Mock UI 能力 Case 的统一细分类规则。"""

from __future__ import annotations

from collections.abc import Iterable
from typing import TypeVar

from .models import ElementCase, InventoryCase, OperationCase


T = TypeVar("T")

OPERATION_CATEGORY_LABELS = {
    "clicks": "点击操作", "inputs": "输入操作", "keyboard": "键盘操作",
    "mouse_drag_scroll": "鼠标拖拽与滚动", "form_controls": "表单控件",
    "files_screenshots": "文件与截图", "waits": "等待机制",
    "browser_navigation": "浏览器与页签导航", "browser_context": "浏览器上下文",
    "reads": "信息读取", "events_visuals": "事件与视觉辅助", "assertions": "元素断言",
}

OPERATION_CATEGORY_METHODS = {
    "clicks": {"w_click", "w_dblclick", "w_force_click", "w_many_click", "w_right_click", "w_time_click", "w_tap", "w_mouse_click", "w_mouse_click_center", "w_mouse_dblclick", "w_mouse_right_click"},
    "inputs": {"w_input", "w_clear_input", "w_clear", "w_type", "w_press_sequentially", "w_get_input_value", "w_keyboard_type_text", "w_keyboard_insert_text", "w_keyboard_delete_text"},
    "keyboard": {"w_press", "w_keys", "w_keyboard_down", "w_keyboard_up", "w_keyboard_shortcut"},
    "mouse_drag_scroll": {"w_hover", "w_scroll_to_element", "w_drag_up_pixel", "w_drag_down_pixel", "w_drag_left_pixel", "w_drag_right_pixel", "w_drag_to", "w_wheel", "w_mouse_move_center", "w_mouse_move", "w_mouse_down", "w_mouse_up", "w_mouse_wheel_xy"},
    "form_controls": {"w_focus", "w_blur", "w_check", "w_uncheck", "w_set_checked", "w_select_option", "w_select_text"},
    "files_screenshots": {"w_upload_files", "w_download", "w_ele_screenshot", "w_screenshot"},
    "waits": {"w_wait_for_element_state", "w_wait_for_timeout", "w_wait_for_load_state", "w_wait_for_url", "w_wait_for_selector", "w_wait_for_function"},
    "browser_navigation": {"w_goto", "w_switch_tabs", "w_close_current_tab", "w_open_new_tab_and_switch", "w_refresh", "w_go_back", "w_go_forward", "w_new_page", "w_close_page_by_index", "w_switch_latest_tab"},
    "browser_context": {"w_accept_dialog", "w_dismiss_dialog", "w_set_cookie", "w_clear_cookies", "w_clear_storage", "w_set_viewport_size", "w_set_extra_http_headers", "w_add_init_script", "w_evaluate", "w_grant_permissions", "w_clear_permissions"},
    "reads": {"w_get_text", "w_get_attribute", "w_get_inner_html", "w_get_texts", "w_get_cookie", "w_get_title", "w_get_url", "w_content"},
    "events_visuals": {"w_dispatch_event", "w_highlight"},
    "assertions": {"w_to_have_count", "a_assert_ele_exists", "w_to_element_count", "w_not_to_contain_text", "w_not_to_be_empty", "w_not_to_be_enabled", "w_not_to_be_focused", "w_not_to_be_hidden", "w_not_to_be_in_viewport", "w_not_to_be_visible", "w_not_to_have_class", "w_to_be_checked", "w_to_be_disabled", "w_to_be_enabled", "w_to_be_editable", "w_to_be_empty", "w_to_be_visible"},
}

ELEMENT_CATEGORY_LABELS = {
    "clicks": "点击控件", "inputs": "输入控件", "selections": "选择控件",
    "uploads": "文件上传控件", "states": "控件状态",
}
ELEMENT_METHOD_CATEGORIES = {
    "w_click": "clicks", "w_input": "inputs", "w_select_option": "selections",
    "w_check": "selections", "w_upload_files": "uploads", "w_to_be_disabled": "states",
}
INVENTORY_PAGE_LABELS = {
    "global": "全局导航", "scenariosPage": "场景编排", "httpPage": "HTTP 业务",
    "componentsPage": "组件实验室", "ssePage": "SSE 事件流",
    "websocketPage": "WebSocket 双向通信", "mcpPage": "MCP 协议", "grpcPage": "gRPC 协议",
}


def _group(cases: Iterable[T], classifier, labels: dict[str, str]) -> dict[str, tuple[T, ...]]:
    grouped: dict[str, list[T]] = {key: [] for key in labels}
    unknown: list[str] = []
    for case in cases:
        key = classifier(case)
        if key not in grouped:
            unknown.append(str(getattr(case, "case_id", case)))
        else:
            grouped[key].append(case)
    if unknown:
        raise ValueError(f"UI Case 缺少细分类规则：{', '.join(unknown)}")
    empty = [key for key, values in grouped.items() if not values]
    if empty:
        raise ValueError(f"UI Case 细分类为空：{', '.join(empty)}")
    return {key: tuple(values) for key, values in grouped.items()}


def group_operation_cases(cases: Iterable[OperationCase]) -> dict[str, tuple[OperationCase, ...]]:
    categories = {method: category for category, methods in OPERATION_CATEGORY_METHODS.items() for method in methods}
    return _group(cases, lambda case: categories.get(case.method), OPERATION_CATEGORY_LABELS)


def group_element_cases(cases: Iterable[ElementCase]) -> dict[str, tuple[ElementCase, ...]]:
    return _group(cases, lambda case: ELEMENT_METHOD_CATEGORIES.get(case.method), ELEMENT_CATEGORY_LABELS)


def group_inventory_cases(cases: Iterable[InventoryCase]) -> dict[str, tuple[InventoryCase, ...]]:
    return _group(cases, lambda case: case.page_key, INVENTORY_PAGE_LABELS)


__all__ = ["ELEMENT_CATEGORY_LABELS", "INVENTORY_PAGE_LABELS", "OPERATION_CATEGORY_LABELS", "group_element_cases", "group_inventory_cases", "group_operation_cases"]

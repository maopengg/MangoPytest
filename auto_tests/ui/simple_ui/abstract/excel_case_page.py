"""新版 Mango Mock UI 的 Excel 用例执行页面对象。"""

import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from mangoautomation.uidrives import BaseData, SyncWebDevice
from mangoautomation.uidrives.web import SyncWebAssertion
from playwright.sync_api import Locator, TimeoutError as PlaywrightTimeoutError

from auto_tests.ui.simple_ui.config import settings
from auto_tests.ui.simple_ui.elements import elements
from auto_tests.ui.simple_ui.excel_cases.models import ElementCase, InventoryCase, OperationCase
from core.utils import log, project_dir


class ExcelCasePage(SyncWebDevice):
    """把 Excel 中的方法名、元素 ID 和参数转换成实际同步 Web 操作。"""

    PAGE_NAVIGATION = {
        "scenariosPage": "nav-scenarios",
        "httpPage": "nav-business",
        "ssePage": "nav-sse",
        "websocketPage": "nav-websocket",
        "mcpPage": "nav-mcp",
        "grpcPage": "nav-grpc",
        "componentsPage": "nav-components",
    }
    PAGE_CONTAINERS = {
        "scenariosPage": "scenarios-page",
        "httpPage": "business-page",
        "ssePage": "sse-page",
        "websocketPage": "websocket-page",
        "mcpPage": "mcp-page",
        "grpcPage": "grpc-page",
        "componentsPage": "components-page",
    }
    LOCATOR_METHODS = {
        "w_blur", "w_check", "w_clear", "w_clear_input", "w_click", "w_dblclick",
        "w_dispatch_event", "w_download", "w_drag_down_pixel", "w_drag_left_pixel",
        "w_drag_right_pixel", "w_drag_up_pixel", "w_ele_screenshot", "w_focus",
        "w_force_click", "w_get_attribute", "w_get_inner_html", "w_get_input_value",
        "w_get_text", "w_get_texts", "w_highlight", "w_hover", "w_input",
        "w_many_click", "w_open_new_tab_and_switch", "w_press", "w_press_sequentially",
        "w_right_click", "w_scroll_to_element", "w_select_option", "w_select_text",
        "w_set_checked", "w_tap", "w_time_click", "w_type", "w_uncheck",
        "w_upload_files", "w_wait_for_element_state",
    }
    ASSERTION_METHODS = {
        "a_assert_ele_exists", "w_not_to_be_empty", "w_not_to_be_enabled",
        "w_not_to_be_focused", "w_not_to_be_hidden", "w_not_to_be_in_viewport",
        "w_not_to_be_visible", "w_not_to_contain_text", "w_not_to_have_class",
        "w_to_be_checked", "w_to_be_disabled", "w_to_be_editable", "w_to_be_empty",
        "w_to_be_enabled", "w_to_be_visible", "w_to_element_count", "w_to_have_count",
    }
    AUTH_TARGETS = {
        "switch-login", "cleanup-run", "order-product", "load-products", "create-order",
        "pay-order", "refund-order", "create-claim", "query-claim", "approve-claim",
        "start-review", "poll-review", "cancel-review", "connect-sse", "disconnect-sse",
        "connect-ws", "send-ws", "ping-ws", "subscribe-ws", "unsubscribe-ws",
        "burst-ws", "slow-consumer-ws", "disconnect-ws", "send-custom-ws",
    }
    ELEMENT_METHOD_OVERRIDES = {
        "double-click-target": "w_dblclick",
        "force-click-target": "w_force_click",
        "hover-target": "w_hover",
        "right-click-target": "w_right_click",
        "tap-target": "w_tap",
        "dispatch-event-target": "w_dispatch_event",
        "coordinate-pad": "w_mouse_click_center",
        "scroll-operation-target": "w_scroll_to_element",
    }

    def __init__(self, base_data: BaseData):
        self.base_data = base_data
        self.web_ass = SyncWebAssertion(base_data)
        self.run_created = False
        # w_highlight 兼容执行器完整链路中才会注入的两个属性。
        self.element_result_model = None
        self.element_model = SimpleNamespace(name="Excel data-testid")
        super().__init__(base_data)

    @property
    def page(self):
        return self.base_data.page

    def locator(self, element_id: str) -> Locator:
        return elements.locate(self.page, element_id)

    def goto(self) -> None:
        log.info(f"打开 Mango Mock UI：{settings.BASE_URL}")
        self.w_goto(settings.BASE_URL)
        self.w_wait_for_load_state("domcontentloaded", 30000)
        self.locator("app-header").wait_for(state="visible")

    def open_page(self, page_key: str) -> None:
        if page_key in ("", "global"):
            return
        navigation_id = self.PAGE_NAVIGATION.get(page_key)
        container_id = self.PAGE_CONTAINERS.get(page_key)
        if navigation_id is None or container_id is None:
            raise ValueError(f"Excel 中存在未知页面标识：{page_key}")
        self.w_click(self.locator(navigation_id))
        self.locator(container_id).wait_for(state="visible")

    def execute_operation(self, case: OperationCase) -> Any:
        self.goto()
        self.open_page("componentsPage")
        params = self._expand(case.params)
        target = self._operation_target(case)
        self._prepare_operation(case, target, params)
        result = self._invoke(case.method, target, params)
        self._complete_operation(case)
        self._verify_operation(case, target, result, params)
        return result

    def execute_element(self, case: ElementCase) -> None:
        self.goto()
        self._prepare_element_case(case)
        target = self.locator(case.element_id)
        target.wait_for(state="attached")
        if case.element_id == "skip-to-content":
            # 无障碍跳转链接默认位于视口外，获得焦点后才显示。
            self.w_focus(target)
        method, params = self._element_method_and_params(case)
        before = self._safe_state(target)
        result = self._invoke(method, target, params)
        if case.element_id == "create-run-login":
            self.page.wait_for_function(
                "() => document.querySelector('[data-testid=\"current-run-id\"]')?.textContent !== '未创建'",
                timeout=10000,
            )
            self.run_created = True
        elif case.element_id == "cleanup-run":
            self._wait_for_business_state(
                "() => document.querySelector('[data-testid=\"current-run-id\"]')?.textContent === '未创建'",
                "清理测试运行",
            )
            self.run_created = False
        self._verify_element(case, target, method, params, before, result)

    def verify_inventory(self, case: InventoryCase) -> None:
        self.goto()
        self.open_page(case.page_key)
        target = self.locator(case.element_id)
        count = target.count()
        assert count == 1, f"{case.element_id} 应唯一存在，实际匹配 {count} 个"
        actual_tag = target.first.evaluate("element => element.tagName.toLowerCase()")
        assert actual_tag == case.tag, f"{case.element_id} 标签期望 {case.tag}，实际 {actual_tag}"
        assert target.first.get_attribute("data-testid") == case.element_id

    def cleanup_run(self) -> None:
        if not self.run_created or self.page.is_closed():
            return
        try:
            self.open_page("httpPage")
            self.w_click(self.locator("cleanup-run"))
            self.page.wait_for_function(
                "() => document.querySelector('[data-testid=\"current-run-id\"]')?.textContent === '未创建'",
                timeout=5000,
            )
            self.run_created = False
        except PlaywrightTimeoutError as error:
            log.warning(f"UI 测试运行清理超时：{error}")

    def _prepare_operation(self, case: OperationCase, target: Locator, params: dict[str, Any]) -> None:
        if case.method.startswith("w_keyboard") or case.method == "w_keys":
            self.w_focus(self.locator("keyboard-target"))
        if case.method in {"w_get_input_value", "w_keyboard_delete_text"}:
            self.w_input(self.locator("keyboard-target"), "AUTO_KEYBOARD_VALUE")
            self.w_focus(self.locator("keyboard-target"))
        if case.method == "w_mouse_wheel_xy":
            self.w_scroll_to_element(self.locator("scroll-operation-target"))
        if case.method in {
            "w_mouse_click", "w_mouse_move", "w_mouse_dblclick", "w_mouse_right_click",
        }:
            box = self.locator("coordinate-pad").bounding_box()
            assert box is not None, "coordinate-pad 不可见，无法计算鼠标坐标"
            params["x"] = round(box["x"] + box["width"] / 2)
            params["y"] = round(box["y"] + box["height"] / 2)
        if case.method in {"w_mouse_down", "w_mouse_up"}:
            box = self.locator("coordinate-pad").bounding_box()
            assert box is not None, "coordinate-pad 不可见，无法准备鼠标位置"
            self.page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
        if case.method in {"w_switch_tabs", "w_close_current_tab"}:
            new_page = self.base_data.context.new_page()
            new_page.goto(f"{settings.BASE_URL}/static/iframe.html?source=excel-prepare")
            new_page.bring_to_front()
            self.base_data.page = new_page
            if case.method == "w_switch_tabs":
                params["individual"] = 2
        if case.method in {"w_close_page_by_index", "w_switch_latest_tab"}:
            self.base_data.context.new_page()
            if case.method == "w_close_page_by_index":
                params["individual"] = 2
        if case.method == "w_go_back":
            self.w_click(self.locator("push-history-state"))
        if case.method == "w_go_forward":
            self.w_click(self.locator("push-history-state"))
            self.w_go_back()
        if case.method == "w_set_cookie":
            params["storage_state"] = json.dumps(params["storage_state"], ensure_ascii=False)
        if case.method in {"w_get_cookie", "w_clear_cookies", "w_clear_storage"}:
            self.w_click(self.locator("seed-browser-storage"))
        if case.method == "w_wait_for_timeout":
            # mangoautomation 此方法以秒为单位，Excel 里的 300 表示毫秒。
            params["_time"] = 1
        if case.method == "w_tap":
            target.scroll_into_view_if_needed()
        if case.method == "w_open_new_tab_and_switch":
            params.pop("target_element_id", None)

    def _complete_operation(self, case: OperationCase) -> None:
        if case.method in {"w_accept_dialog", "w_dismiss_dialog"}:
            self.w_click(self.locator("native-confirm"))
        elif case.method == "w_add_init_script":
            self.w_goto(settings.BASE_URL)

    def _verify_operation(
        self,
        case: OperationCase,
        target: Locator,
        result: Any,
        params: dict[str, Any],
    ) -> None:
        if case.method in {
            "w_get_text", "w_get_attribute", "w_get_input_value", "w_get_inner_html",
            "w_get_texts", "w_evaluate", "w_get_title", "w_get_url", "w_content",
        }:
            assert result not in (None, "", []), f"{case.method} 应返回有效结果"
        elif case.method in {"w_ele_screenshot", "w_screenshot"}:
            assert Path(params["path"]).is_file(), f"截图文件未生成：{params['path']}"
        elif case.method == "w_download":
            download_path = self.base_data.test_data.get_cache(params["file_key"])
            assert download_path and Path(download_path).is_file(), "下载文件未生成"
        elif case.method == "w_get_cookie":
            assert Path(self.base_data.download_path, "storage_state.json").is_file()
        elif case.method == "w_set_cookie":
            assert any(cookie["name"] == "ui_case" for cookie in self.base_data.context.cookies())
        elif case.method == "w_clear_cookies":
            assert not self.base_data.context.cookies()
        elif case.method == "w_clear_storage":
            storage = self.page.evaluate(
                "() => [localStorage.getItem('mango-ui-local'), sessionStorage.getItem('mango-ui-session')]"
            )
            assert storage == [None, None]
        elif case.method == "w_add_init_script":
            assert self.page.evaluate("() => window.__mangoAutomationInit") is True
        elif case.method in {"w_input", "w_clear_input"}:
            assert target.input_value() == str(params["input_value"])
        elif case.method == "w_clear":
            assert target.input_value() == ""
        elif case.method in {"w_check", "w_set_checked"}:
            assert target.is_checked()
        elif case.method == "w_uncheck":
            assert not target.is_checked()
        elif case.method == "w_select_option":
            assert params["values"] in target.input_value()
        elif case.method in self.ASSERTION_METHODS:
            assert result is not None, f"{case.method} 未返回断言结果"
        elif case.method in {"w_accept_dialog", "w_dismiss_dialog"}:
            text = self.locator("native-dialog-result").inner_text()
            expected = "接受" if case.method == "w_accept_dialog" else "取消"
            assert expected in text
        else:
            assert target.count() >= 1 or case.method in {
                "w_close_current_tab", "w_close_page_by_index", "w_new_page",
            }

    def _prepare_element_case(self, case: ElementCase) -> None:
        if case.element_id in {"modal-input", "cancel-modal", "confirm-modal"}:
            self.open_page("componentsPage")
            self.w_click(self.locator("open-modal"))
            self.locator("demo-modal").wait_for(state="visible")
            return
        if case.element_id in self.AUTH_TARGETS:
            self._bootstrap_business()
        self.open_page(case.page_key)
        if case.element_id == "order-product":
            self.w_click(self.locator("load-products"))
            self.page.wait_for_function(
                "() => Boolean(document.querySelector('[data-testid=\"order-product\"]')?.value)",
            )
        elif case.element_id in {"create-order", "pay-order", "refund-order"}:
            self._prepare_order(case.element_id)
        elif case.element_id in {"query-claim", "approve-claim"}:
            self._prepare_claim()
        elif case.element_id in {"poll-review", "cancel-review"}:
            self._prepare_review()
        elif case.element_id in {
            "send-ws", "ping-ws", "subscribe-ws", "unsubscribe-ws", "burst-ws",
            "slow-consumer-ws", "disconnect-ws", "send-custom-ws",
        }:
            self._connect_websocket()
        elif case.element_id == "disconnect-sse":
            self.w_click(self.locator("connect-sse"))
            self.page.wait_for_timeout(300)
        elif case.element_id == "upload-files":
            self.w_upload_files(self.locator("ui-file-input"), self._upload_file())
        elif case.element_id == "validate-form":
            self.w_input(self.locator("required-text"), "AUTO_UI_CASE")
        elif case.element_id in {"tree-leaf-scenario", "tree-leaf-trace"}:
            target = self.locator(case.element_id)
            target.evaluate("element => { for (const item of element.closest('details').parentElement.querySelectorAll('details')) item.open = true; }")

    def _element_method_and_params(self, case: ElementCase) -> tuple[str, dict[str, Any]]:
        method = case.method
        params = self._expand(case.params)
        method = self.ELEMENT_METHOD_OVERRIDES.get(case.element_id, method)
        if case.element_id == "dispatch-event-target":
            params = {"event_type": "click", "event_init": {"bubbles": True}}
        if method == "w_check":
            params.pop("checked", None)
        if case.element_id == "order-product":
            params = {"values": self.locator("order-product").locator("option").first.get_attribute("value")}
        if case.element_id in {"native-alert", "native-confirm", "native-prompt"}:
            self.page.once(
                "dialog",
                lambda dialog: dialog.accept("AUTO_UI_CASE") if dialog.type == "prompt" else dialog.accept(),
            )
        return method, params

    def _operation_target(self, case: OperationCase) -> Locator:
        target = self.locator(case.target_id)
        if case.method == "w_many_click" and case.target_id == "many-click-targets":
            return target.locator("button")
        if (
            case.method in {"w_get_texts", "w_to_have_count", "w_to_element_count"}
            and case.target_id == "multiple-text-targets"
        ):
            return target.locator("span")
        return target

    def _verify_element(
        self,
        case: ElementCase,
        target: Locator,
        method: str,
        params: dict[str, Any],
        before: dict[str, Any],
        result: Any,
    ) -> None:
        if method in {"w_input", "w_clear_input"}:
            assert target.input_value() == str(params["input_value"])
        elif method == "w_select_option":
            expected = params["values"]
            assert expected in target.input_value()
        elif method in {"w_check", "w_set_checked"}:
            assert target.is_checked()
        elif method == "w_to_be_disabled":
            assert result is not None and target.is_disabled()
        elif method == "w_hover":
            assert target.count() == 1
        else:
            after = self._safe_state(target)
            assert before["count"] == 1
            assert after["count"] in {0, 1} or len(self.base_data.context.pages) > 1

    def _invoke(self, method: str, target: Locator, params: dict[str, Any]) -> Any:
        if method in self.ASSERTION_METHODS:
            return getattr(self.web_ass, method)(target, **params)
        operation = getattr(self, method, None)
        if not callable(operation):
            raise AttributeError(f"mangoautomation 不支持 Excel 方法：{method}")
        if method == "w_drag_to":
            target_id = params.pop("target_element_id")
            return operation(target, self.locator(target_id))
        if method in self.LOCATOR_METHODS:
            return operation(target, **params)
        return operation(**params)

    def _bootstrap_business(self) -> None:
        if self.run_created:
            return
        self.open_page("httpPage")
        self.w_clear_input(self.locator("run-name"), "AUTO_UI_EXCEL")
        self.w_clear_input(self.locator("run-seed"), "20260823")
        self.w_select_option(self.locator("login-username"), "employee")
        self.w_clear_input(self.locator("login-password"), "password123")
        self.w_click(self.locator("create-run-login"))
        self.page.wait_for_function(
            "() => document.querySelector('[data-testid=\"current-run-id\"]')?.textContent !== '未创建'",
            timeout=10000,
        )
        self.page.wait_for_function(
            "() => document.querySelector('[data-testid=\"current-user\"]')?.textContent !== '未登录'",
            timeout=10000,
        )
        self.run_created = True

    def _prepare_order(self, target_id: str) -> None:
        self.w_click(self.locator("load-products"))
        self.page.wait_for_function(
            "() => Boolean(document.querySelector('[data-testid=\"order-product\"]')?.value)",
        )
        if target_id == "create-order":
            return
        self.w_click(self.locator("create-order"))
        self._wait_for_business_state(
            "() => document.querySelector('[data-testid=\"order-id\"]')?.textContent !== '-'",
            "创建订单",
        )
        if target_id == "refund-order":
            self.w_click(self.locator("pay-order"))
            self.page.wait_for_function(
                "() => document.querySelector('[data-testid=\"order-status\"]')?.textContent === 'paid'",
                timeout=10000,
            )

    def _prepare_claim(self) -> None:
        self.w_click(self.locator("create-claim"))
        self.page.wait_for_function(
            "() => document.querySelector('[data-testid=\"claim-id\"]')?.textContent !== '-'",
            timeout=10000,
        )

    def _prepare_review(self) -> None:
        self.w_click(self.locator("start-review"))
        self.page.wait_for_function(
            "() => !document.querySelector('[data-testid=\"review-status\"]')?.textContent.startsWith('未开始')",
            timeout=10000,
        )

    def _connect_websocket(self) -> None:
        self.w_click(self.locator("connect-ws"))
        self.page.wait_for_function(
            "() => document.querySelector('[data-testid=\"ws-messages\"]')?.textContent !== '未连接'",
            timeout=10000,
        )

    def _wait_for_business_state(self, expression: str, action: str) -> None:
        try:
            self.page.wait_for_function(expression, timeout=10000)
        except PlaywrightTimeoutError as error:
            result = self.locator("business-result").inner_text()
            raise AssertionError(f"{action}未达到预期状态，页面返回：{result}") from error

    def _expand(self, value: Any) -> Any:
        if isinstance(value, dict):
            return {key: self._expand(item) for key, item in value.items()}
        if isinstance(value, list):
            return [self._expand(item) for item in value]
        if not isinstance(value, str):
            return value
        replacements = {
            "${project_root}": project_dir.root_path(),
            "${screenshot_dir}": str(Path(self.base_data.screenshot_path).resolve()),
            "${test_run_id}": "AUTO_UI_EXCEL",
        }
        result = value
        for source, replacement in replacements.items():
            result = result.replace(source, str(replacement))
        return result

    @staticmethod
    def _safe_state(target: Locator) -> dict[str, Any]:
        count = target.count()
        if count == 0:
            return {"count": 0, "visible": False}
        return {"count": count, "visible": target.first.is_visible()}

    @staticmethod
    def _upload_file() -> str:
        return str(Path(__file__).resolve().parents[1] / "data" / "upload.txt")

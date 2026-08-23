"""能力验证执行层的同步 Web 基类。"""

from pathlib import Path
from types import SimpleNamespace
from typing import Any

from mangoautomation.uidrives import BaseData, SyncWebDevice
from mangoautomation.uidrives.web import SyncWebAssertion
from playwright.sync_api import Locator

from auto_tests.ui.bdd_ui.config import settings
from auto_tests.ui.bdd_ui.elements import elements
from core.utils import log, project_dir


class BddUICapabilityBase(SyncWebDevice):
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

    def __init__(self, base_data: BaseData, data_factory=None):
        self.base_data = base_data
        self.data_factory = data_factory
        self.web_ass = SyncWebAssertion(base_data)
        self.run_created = False
        self.element_result_model = None
        self.element_model = SimpleNamespace(name="bdd data-testid")
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
            raise ValueError(f"用例清单中存在未知页面标识：{page_key}")
        self.w_click(self.locator(navigation_id))
        self.locator(container_id).wait_for(state="visible")

    def _invoke(self, method: str, target: Locator, params: dict[str, Any]) -> Any:
        if method in self.ASSERTION_METHODS:
            return getattr(self.web_ass, method)(target, **params)
        operation = getattr(self, method, None)
        if not callable(operation):
            raise AttributeError(f"mangoautomation 不支持用例方法：{method}")
        if method == "w_drag_to":
            target_id = params.pop("target_element_id")
            return operation(target, self.locator(target_id))
        if method in self.LOCATOR_METHODS:
            return operation(target, **params)
        return operation(**params)

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
            "${test_run_id}": "AUTO_BDD_UI",
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


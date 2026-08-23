"""交互元素能力用例执行器。"""

from typing import Any

from playwright.sync_api import Locator

from auto_tests.ui.bdd_ui.cases.models import ElementCase


class ElementCaseMixin:
    def execute_element(self, case: ElementCase) -> None:
        self.goto()
        self._prepare_element_case(case)
        target = self.locator(case.element_id)
        target.wait_for(state="attached")
        if case.element_id == "skip-to-content":
            self.w_focus(target)
        method, params = self._element_method_and_params(case)
        before = self._safe_state(target)
        result = self._invoke(method, target, params)
        if case.element_id == "create-run-login":
            self.page.wait_for_function(
                "() => document.querySelector('[data-testid=\"current-run-id\"]')"
                "?.textContent !== '未创建'",
                timeout=10000,
            )
            self.run_created = True
        elif case.element_id == "cleanup-run":
            self._wait_for_business_state(
                "() => document.querySelector('[data-testid=\"current-run-id\"]')"
                "?.textContent === '未创建'",
                "清理测试运行",
            )
            self.run_created = False
            if self.data_factory is not None:
                self.data_factory.mark_deleted()
        elif case.element_id in {"pay-order", "refund-order"}:
            expected = "paid" if case.element_id == "pay-order" else "refunded"
            self.page.wait_for_function(
                "value => document.querySelector('[data-testid=\"order-status\"]')"
                "?.textContent === value",
                arg=expected,
                timeout=10000,
            )
        elif case.element_id in {"query-claim", "approve-claim"}:
            self.page.wait_for_function(
                "() => document.querySelector('[data-testid=\"claim-status\"]')"
                "?.textContent !== '-'",
                timeout=10000,
            )
        self._verify_element(case, target, method, params, before, result)

    def _prepare_element_case(self, case: ElementCase) -> None:
        if case.element_id in {"modal-input", "cancel-modal", "confirm-modal"}:
            self.open_page("componentsPage")
            self.w_click(self.locator("open-modal"))
            self.locator("demo-modal").wait_for(state="visible")
            return
        if case.element_id in self.AUTH_TARGETS:
            self._prepare_factory_data(case.element_id)
        self.open_page(case.page_key)
        if case.element_id == "order-product":
            self.w_click(self.locator("load-products"))
            self.page.wait_for_function(
                "() => Boolean(document.querySelector('[data-testid=\"order-product\"]')"
                "?.value)",
            )
        elif case.element_id == "create-order":
            self._prepare_order(case.element_id)
        elif (
            case.element_id in {"pay-order", "refund-order"}
            and self.data_factory is None
        ):
            self._prepare_order(case.element_id)
        elif case.element_id in {"query-claim", "approve-claim"}:
            if self.data_factory is None:
                self._prepare_claim()
        elif case.element_id in {"poll-review", "cancel-review"}:
            if self.data_factory is None:
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
            self.locator(case.element_id).evaluate(
                "element => { for (const item of "
                "element.closest('details').parentElement.querySelectorAll('details')) "
                "item.open = true; }"
            )

    def _element_method_and_params(
        self, case: ElementCase
    ) -> tuple[str, dict[str, Any]]:
        method = self.ELEMENT_METHOD_OVERRIDES.get(case.element_id, case.method)
        params = self._expand(case.params)
        if case.element_id == "dispatch-event-target":
            params = {"event_type": "click", "event_init": {"bubbles": True}}
        if method == "w_check":
            params.pop("checked", None)
        if case.element_id == "order-product":
            option = self.locator("order-product").locator("option").first
            params = {"values": option.get_attribute("value")}
        if case.element_id in {"native-alert", "native-confirm", "native-prompt"}:
            self.page.once(
                "dialog",
                lambda dialog: dialog.accept("AUTO_UI_CASE")
                if dialog.type == "prompt"
                else dialog.accept(),
            )
        return method, params

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
            assert params["values"] in target.input_value()
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


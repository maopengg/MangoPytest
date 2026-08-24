"""能力场景的业务前置编排，统一委托本项目 Data Factory。"""

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from core.utils import log


class BusinessPreconditionMixin:
    def cleanup_run(self) -> None:
        if not self.run_created or self.page.is_closed():
            return
        try:
            self.open_page("httpPage")
            self.element_action("cleanup-run", "w_click")
            self.page.wait_for_function(
                "() => document.querySelector('[data-testid=\"current-run-id\"]')"
                "?.textContent === '未创建'",
                timeout=5000,
            )
            self.run_created = False
        except PlaywrightTimeoutError as error:
            log.warning(f"UI 测试运行清理超时：{error}")

    def _bootstrap_business(self) -> None:
        if self.run_created:
            return
        self.open_page("httpPage")
        self.element_action(
            "run-name",
            "w_clear_input",
            {"input_value": self.run_name_prefix},
        )
        self.element_action("run-seed", "w_clear_input", {"input_value": "20260823"})
        self.element_action("login-username", "w_select_option", {"values": "employee"})
        self.element_action("login-password", "w_clear_input", {"input_value": "password123"})
        self.element_action("create-run-login", "w_click")
        self.page.wait_for_function(
            "() => document.querySelector('[data-testid=\"current-run-id\"]')"
            "?.textContent !== '未创建'",
            timeout=10000,
        )
        self.page.wait_for_function(
            "() => document.querySelector('[data-testid=\"current-user\"]')"
            "?.textContent !== '未登录'",
            timeout=10000,
        )
        self.run_created = True

    def _prepare_factory_data(self, element_id: str) -> None:
        if self.data_factory is None:
            self._bootstrap_business()
            return
        role = "employee"
        if element_id == "pay-order":
            self.data_factory.create_order("pending")
        elif element_id == "refund-order":
            self.data_factory.create_order("paid")
        elif element_id in {"query-claim", "approve-claim"}:
            self.data_factory.create_claim()
            if element_id == "approve-claim":
                role = "dept_manager"
        elif element_id in {"poll-review", "cancel-review"}:
            self.data_factory.create_review()
        else:
            self.data_factory.run(role)
        self.data_factory.bind_browser(self.base_data, role)

    def _prepare_order(self, target_id: str) -> None:
        self.element_action("load-products", "w_click")
        self.page.wait_for_function(
            "() => Boolean(document.querySelector('[data-testid=\"order-product\"]')"
            "?.value)",
        )
        if target_id == "create-order":
            return
        self.element_action("create-order", "w_click")
        self._wait_for_business_state(
            "() => document.querySelector('[data-testid=\"order-id\"]')"
            "?.textContent !== '-'",
            "创建订单",
        )
        if target_id == "refund-order":
            self.element_action("pay-order", "w_click")
            self.page.wait_for_function(
                "() => document.querySelector('[data-testid=\"order-status\"]')"
                "?.textContent === 'paid'",
                timeout=10000,
            )

    def _prepare_claim(self) -> None:
        self.element_action("create-claim", "w_click")
        self.page.wait_for_function(
            "() => document.querySelector('[data-testid=\"claim-id\"]')"
            "?.textContent !== '-'",
            timeout=10000,
        )

    def _prepare_review(self) -> None:
        self.element_action("start-review", "w_click")
        self.page.wait_for_function(
            "() => !document.querySelector('[data-testid=\"review-status\"]')"
            "?.textContent.startsWith('未开始')",
            timeout=10000,
        )

    def _connect_websocket(self) -> None:
        self.element_action("connect-ws", "w_click")
        self.page.wait_for_function(
            "() => document.querySelector('[data-testid=\"ws-messages\"]')"
            "?.textContent !== '未连接'",
            timeout=10000,
        )

    def _wait_for_business_state(self, expression: str, action: str) -> None:
        try:
            self.page.wait_for_function(expression, timeout=10000)
        except PlaywrightTimeoutError as error:
            result = self.locator("business-result").inner_text()
            raise AssertionError(
                f"{action}未达到预期状态，页面返回：{result}"
            ) from error

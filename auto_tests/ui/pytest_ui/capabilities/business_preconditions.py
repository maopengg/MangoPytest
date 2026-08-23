"""能力场景的业务前置编排，统一委托本项目 Data Factory。"""

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from core.utils import log


class BusinessPreconditionMixin:
    def cleanup_run(self) -> None:
        if not self.run_created or self.page.is_closed():
            return
        try:
            self.open_page("httpPage")
            self.w_click(self.locator("cleanup-run"))
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
        self.w_clear_input(self.locator("run-name"), "AUTO_PYTEST_UI")
        self.w_clear_input(self.locator("run-seed"), "20260823")
        self.w_select_option(self.locator("login-username"), "employee")
        self.w_clear_input(self.locator("login-password"), "password123")
        self.w_click(self.locator("create-run-login"))
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
        self.w_click(self.locator("load-products"))
        self.page.wait_for_function(
            "() => Boolean(document.querySelector('[data-testid=\"order-product\"]')"
            "?.value)",
        )
        if target_id == "create-order":
            return
        self.w_click(self.locator("create-order"))
        self._wait_for_business_state(
            "() => document.querySelector('[data-testid=\"order-id\"]')"
            "?.textContent !== '-'",
            "创建订单",
        )
        if target_id == "refund-order":
            self.w_click(self.locator("pay-order"))
            self.page.wait_for_function(
                "() => document.querySelector('[data-testid=\"order-status\"]')"
                "?.textContent === 'paid'",
                timeout=10000,
            )

    def _prepare_claim(self) -> None:
        self.w_click(self.locator("create-claim"))
        self.page.wait_for_function(
            "() => document.querySelector('[data-testid=\"claim-id\"]')"
            "?.textContent !== '-'",
            timeout=10000,
        )

    def _prepare_review(self) -> None:
        self.w_click(self.locator("start-review"))
        self.page.wait_for_function(
            "() => !document.querySelector('[data-testid=\"review-status\"]')"
            "?.textContent.startsWith('未开始')",
            timeout=10000,
        )

    def _connect_websocket(self) -> None:
        self.w_click(self.locator("connect-ws"))
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


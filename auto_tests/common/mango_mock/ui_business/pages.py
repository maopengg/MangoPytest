"""Mango Mock 业务页面对象。"""

from mangoautomation.uidrives import BaseData, SyncWebDevice

from core.ui import configured_element_repository, element_runtime


class MangoMockBusinessPage(SyncWebDevice):
    """绑定项目运行配置的 Mango Mock 业务页面基类。"""

    def __init__(self, base_data: BaseData, settings):
        self.base_data = base_data
        self.settings = settings
        super().__init__(base_data)
        elements = configured_element_repository(settings)
        self.named_elements = element_runtime(base_data, elements, settings)

    @property
    def page(self):
        return self.base_data.page

    def locator(self, key: str):
        return self.named_elements.locator(key)

    def element_action(self, key: str, method: str, params: dict | None = None):
        return self.named_elements.execute(key, method, params)

    def open(self) -> None:
        self.w_goto(self.settings.BASE_URL)
        self.w_wait_for_load_state("domcontentloaded", 30000)
        self.locator("app-header").wait_for(state="visible")
        self.element_action("nav-business", "w_click")
        self.locator("business-page").wait_for(state="visible")


class OrderPage(MangoMockBusinessPage):
    def pay(self) -> str:
        self.element_action("pay-order", "w_click")
        self._wait_status("paid")
        return self.status()

    def refund(self) -> str:
        self.element_action("refund-order", "w_click")
        self._wait_status("refunded")
        return self.status()

    def status(self) -> str:
        return self.locator("order-status").inner_text()

    def _wait_status(self, expected: str) -> None:
        self.page.wait_for_function(
            "value => document.querySelector('[data-testid=\"order-status\"]')"
            "?.textContent === value",
            arg=expected,
            timeout=10000,
        )


class ClaimPage(MangoMockBusinessPage):
    def approve_current_stage(self) -> str:
        previous = self.current_stage()
        self.element_action("approve-claim", "w_click")
        self.page.wait_for_function(
            "value => document.querySelector('[data-testid=\"claim-stage\"]')"
            "?.textContent !== value",
            arg=previous,
            timeout=10000,
        )
        return self.current_stage()

    def current_stage(self) -> str:
        return self.locator("claim-stage").inner_text()

    def status(self) -> str:
        return self.locator("claim-status").inner_text()


class ReviewPage(MangoMockBusinessPage):
    def cancel(self) -> str:
        self.element_action("cancel-review", "w_click")
        self.page.wait_for_function(
            "() => document.querySelector('[data-testid=\"review-status\"]')"
            "?.textContent.startsWith('cancelled')",
            timeout=10000,
        )
        return self.status()

    def status(self) -> str:
        return self.locator("review-status").inner_text().split(" / ", 1)[0]

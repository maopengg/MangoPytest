"""订单业务页面对象。"""

from .base import BusinessPage


class OrderPage(BusinessPage):
    def pay(self) -> str:
        self.w_click(self.locator("pay-order"))
        self._wait_status("paid")
        return self.status()

    def refund(self) -> str:
        self.w_click(self.locator("refund-order"))
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


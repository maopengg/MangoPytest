"""合同评审页面对象。"""

from .base import BusinessPage


class ReviewPage(BusinessPage):
    def cancel(self) -> str:
        self.w_click(self.locator("cancel-review"))
        self.page.wait_for_function(
            "() => document.querySelector('[data-testid=\"review-status\"]')"
            "?.textContent.startsWith('cancelled')",
            timeout=10000,
        )
        return self.status()

    def status(self) -> str:
        return self.locator("review-status").inner_text().split(" / ", 1)[0]


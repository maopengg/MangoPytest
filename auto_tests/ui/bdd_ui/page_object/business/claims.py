"""报销审批页面对象。"""

from .base import BusinessPage


class ClaimPage(BusinessPage):
    def approve_current_stage(self) -> str:
        previous = self.current_stage()
        self.w_click(self.locator("approve-claim"))
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


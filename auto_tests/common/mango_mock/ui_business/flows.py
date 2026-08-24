"""Mango Mock 业务 UI Flow。"""

from .pages import ClaimPage, OrderPage, ReviewPage


class OrderFlow:
    def __init__(self, page: OrderPage):
        self.page = page

    def pay(self) -> str:
        self.page.open()
        return self.page.pay()

    def refund(self) -> str:
        self.page.open()
        return self.page.refund()


class ClaimFlow:
    def __init__(self, page: ClaimPage):
        self.page = page

    def approve_current_stage(self) -> str:
        self.page.open()
        return self.page.approve_current_stage()


class ReviewFlow:
    def __init__(self, page: ReviewPage):
        self.page = page

    def cancel(self) -> str:
        self.page.open()
        return self.page.cancel()

"""业务页面对象基础能力。"""

from mangoautomation.uidrives import BaseData, SyncWebDevice

from auto_tests.ui.pytest_ui.config import settings
from auto_tests.ui.pytest_ui.elements import elements


class BusinessPage(SyncWebDevice):
    def __init__(self, base_data: BaseData):
        self.base_data = base_data
        super().__init__(base_data)

    @property
    def page(self):
        return self.base_data.page

    def locator(self, key: str):
        return elements.locate(self.page, key)

    def open(self) -> None:
        self.w_goto(settings.BASE_URL)
        self.w_wait_for_load_state("domcontentloaded", 30000)
        self.locator("app-header").wait_for(state="visible")
        self.w_click(self.locator("nav-business"))
        self.locator("business-page").wait_for(state="visible")


from playwright.sync_api import Page, BrowserContext

from tools.base_page.web.device_Input import PlaywrightDeviceInput
from tools.base_page.web.element_operation import PlaywrightElementOperation
from tools.base_page.web.operation_browser import PlaywrightOperationBrowser
from tools.base_page.web.operation_page import PlaywrightPageOperation
from tools.data_processor import DataProcessor


class WebDevice(PlaywrightPageOperation, PlaywrightOperationBrowser, PlaywrightElementOperation, PlaywrightDeviceInput):

    def __init__(self, page: Page, context: BrowserContext, data_processor: DataProcessor):
        self.page: Page = page
        self.context: BrowserContext = context
        self.data_processor = data_processor
